"""
============================================================
TradePilotAI Operating System
Trading Application
============================================================

Main orchestrator for the TradePilotAI OS.
It wires the trading workflow into the OS service manager,
dependency injection container, and configuration manager.
"""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stages import (
    BrokerStage,
    DataStage,
    IndicatorStage,
    PortfolioStage,
    RiskStage,
    ScannerStage,
    SignalStage,
    StrategyStage,
)
from tradepilotai_os.pipeline.trading_pipeline import TradingPipeline

from .config_manager import ConfigManager
from .container import Container
from .data_engine import DataEngine
from .registry import ServiceRegistry
from .service_manager import ServiceManager


class TradingApplication:
    """
    Main application controller for the TradePilotAI OS.

    The application lifecycle remains in this class, while the
    trading workflow is delegated to an injected pipeline.
    """

    def __init__(self, config_file: str | None = None) -> None:
        self.container = Container()
        self.registry = ServiceRegistry(self.container)
        self.service_manager = ServiceManager()

        self.config = ConfigManager()
        if config_file is not None:
            self.config.load(config_file)

        self.container.register_singleton("config", self.config)
        self.container.register_singleton("container", self.container)
        self.container.register_singleton("service_manager", self.service_manager)
        self.container.register_singleton("registry", self.registry)

        self.data_engine = DataEngine()
        self.service_manager.register(self.data_engine)
        self.container.register_singleton("data_engine", self.data_engine)

        self._initialize_services()
        self.pipeline = self._build_pipeline()

    def _initialize_services(self) -> None:
        """Initialize the trading services used by the orchestrator."""

        try:
            from src.indicators.indicator_engine import IndicatorEngine
            from src.scanner.market_scanner import MarketScanner
            from src.signals.signal_engine import SignalEngine
            from src.strategy.strategy_engine import StrategyEngine
        except Exception:
            IndicatorEngine = None
            MarketScanner = None
            SignalEngine = None
            StrategyEngine = None

        self.indicator_engine = IndicatorEngine() if IndicatorEngine is not None else None
        self.signal_engine = SignalEngine() if SignalEngine is not None else None
        self.strategy_engine = StrategyEngine() if StrategyEngine is not None else None
        self.scanner = MarketScanner() if MarketScanner is not None else None

        self.risk_engine = self.container.resolve("risk_engine") if self.container.contains("risk_engine") else None
        self.portfolio_manager = self.container.resolve("portfolio_manager") if self.container.contains("portfolio_manager") else None
        self.broker = self.container.resolve("broker") if self.container.contains("broker") else None

        if self.indicator_engine is not None:
            self.container.register_singleton("indicator_engine", self.indicator_engine)
        if self.signal_engine is not None:
            self.container.register_singleton("signal_engine", self.signal_engine)
        if self.strategy_engine is not None:
            self.container.register_singleton("strategy_engine", self.strategy_engine)
        if self.scanner is not None:
            self.container.register_singleton("scanner", self.scanner)

        if self.risk_engine is None:
            from tradepilotai_os.risk.risk_engine import RiskEngine

            self.risk_engine = RiskEngine()
            self.container.register_singleton("risk_engine", self.risk_engine)

        if self.portfolio_manager is None:
            from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager

            self.portfolio_manager = PortfolioManager(initial_cash=100000.0)
            self.container.register_singleton("portfolio_manager", self.portfolio_manager)

        if self.broker is None:
            from tradepilotai_os.broker.paper_broker import PaperBroker

            self.broker = PaperBroker()
            self.container.register_singleton("broker", self.broker)

    def _build_pipeline(self) -> TradingPipeline:
        """Create the injected trading pipeline."""

        return TradingPipeline(
            stages=[
                ScannerStage(self.container.resolve("scanner")),
                DataStage(self.container.resolve("data_engine")),
                IndicatorStage(self.container.resolve("indicator_engine")),
                SignalStage(self.container.resolve("signal_engine")),
                StrategyStage(self.container.resolve("strategy_engine")),
                RiskStage(self.container.resolve("risk_engine")),
                PortfolioStage(self.container.resolve("portfolio_manager")),
                BrokerStage(self.container.resolve("broker")),
            ]
        )

    def run(self) -> int:
        """Execute the trading workflow through the injected pipeline."""

        if self.scanner is None or self.signal_engine is None or self.strategy_engine is None:
            raise RuntimeError("Trading dependencies are not available.")

        print("=" * 60)
        print("TradePilotAI OS")
        print("=" * 60)

        print()
        print("Loading strategy configuration...")
        print(f"Timeframe : {self.config.strategy['timeframe']}")
        print(f"EMA Fast  : {self.config.strategy['ema_fast']}")
        print(f"EMA Slow  : {self.config.strategy['ema_slow']}")
        print(f"RSI       : {self.config.strategy['rsi_period']}")

        print()
        print("Scanning market...")

        watchlist = self.scanner.get_watchlist()
        aggregate_summary = {
            "symbols_scanned": 0,
            "signals_generated": 0,
            "orders_submitted": 0,
            "orders_executed": 0,
            "orders_rejected": 0,
            "failures": [],
        }

        for ticker in watchlist:
            print()
            print("-" * 60)
            print(f"Scanning {ticker}")

            context = PipelineContext(status="running")
            context.set("symbol", ticker)
            context.set("interval", self.config.strategy["timeframe"])
            context.set("period", "180d")
            context.set("watchlist", watchlist)
            context.set("config", self.config)
            context.set("summary", dict(aggregate_summary))

            try:
                pipeline_result = self.pipeline.run(context)
                symbol_summary = pipeline_result.get("summary", {})
                for key in aggregate_summary:
                    if key == "failures":
                        aggregate_summary[key].extend(symbol_summary.get(key, []))
                    else:
                        aggregate_summary[key] = aggregate_summary.get(key, 0) + symbol_summary.get(key, 0)
            except Exception as error:
                context.mark_failed(str(error))
                aggregate_summary["failures"].append({
                    "symbol": ticker,
                    "error": str(error),
                })

            print(f"Signals found for {ticker}: {context.get('summary', {}).get('signals_generated', 0)}")

        print()
        print("=" * 60)
        print(f"TOTAL SIGNALS FOUND : {aggregate_summary['signals_generated']}")
        print(f"TOTAL ORDERS SUBMITTED : {aggregate_summary['orders_submitted']}")
        print(f"TOTAL ORDERS EXECUTED : {aggregate_summary['orders_executed']}")
        print(f"TOTAL ORDERS REJECTED : {aggregate_summary['orders_rejected']}")
        print("=" * 60)

        self.last_run_summary = aggregate_summary
        return aggregate_summary["signals_generated"]

    def start(self) -> None:
        self.service_manager.start_all()

    def stop(self) -> None:
        self.service_manager.stop_all()

    def resolve(self, name: str) -> Any:
        return self.container.resolve(name)
