"""Service/controller for executing workspace backtests."""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Callable

from tradepilotai_os.core.container import Container

from .comparison import StrategyComparisonEngine
from .strategy_library import StrategyLibraryEngine
from .strategy_library import StrategyRegistry
from .backtest_engine import BacktestEngine
from .portfolio_simulator import PortfolioSimulator
from .result import BacktestResult


class BacktestingService:
    """Execute the existing backtest engine with workspace configuration inputs."""

    def __init__(self, container: Container | None = None, engine: BacktestEngine | None = None) -> None:
        self.container = container
        self.engine = engine or self._resolve_engine()
        self.strategy_registry = StrategyRegistry()
        self.comparison_engine = StrategyComparisonEngine(
            strategy_registry=self.strategy_registry,
            base_engine=self.engine,
        )
        self.logger = self._resolve_logger()

    def run_backtest(
        self,
        configuration: dict[str, Any] | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> BacktestResult:
        config = configuration or {}

        initial_cash = self._parse_currency(config.get("capital"), default=100000.0)
        commission_rate = self._parse_rate(config.get("commission"), default=0.0005)
        spread = self._parse_float(config.get("spread"), default=0.02)
        slippage = self._parse_float(config.get("slippage"), default=0.01)
        period = self._period_from_date_range(config.get("date_range"), default="180d")
        requested_symbols = self._parse_symbols(config.get("symbols")) or self._default_symbols()
        strategy_id = self._parse_strategy_id(config.get("strategy_id"))
        strategy_parameters = self._parse_strategy_parameters(config.get("strategy_parameters"))
        strategy = self._configure_strategy(strategy_id=strategy_id, strategy_parameters=strategy_parameters)
        strategy_metadata = self._strategy_metadata(strategy)
        requested_interval = self._parse_timeframe(config.get("timeframe") or config.get("interval"))
        current_interval = requested_interval or strategy_metadata["primary_timeframe"]

        self._configure_engine(
            initial_cash=initial_cash,
            commission_rate=commission_rate,
            spread=spread,
            slippage=slippage,
        )

        if progress_callback is not None:
            progress_callback("Loading historical data...")
        validation = self._load_market_data(requested_symbols, interval=current_interval, period=period)

        if not validation["loaded_symbols"]:
            result = BacktestResult(
                initial_cash=initial_cash,
                requested_symbols=requested_symbols,
                loaded_symbols=[],
                failed_symbols=validation["failed_symbols"],
                completion_status="failed",
            )
            result.portfolio.metadata.update(
                {
                    "initial_cash": initial_cash,
                    "commission_rate": commission_rate,
                    "bid_ask_spread": spread,
                    "slippage": slippage,
                    "strategy_id": strategy_id,
                    "strategy_name": strategy_metadata["name"],
                    "strategy_asset_class": strategy_metadata["asset_class"],
                    "strategy_primary_timeframe": strategy_metadata["primary_timeframe"],
                    "strategy_supported_timeframes": strategy_metadata["supported_timeframes"],
                    "current_timeframe": current_interval,
                    "timeframe_override": requested_interval is not None,
                    "strategy_parameters": strategy_parameters,
                }
            )
            result.portfolio = self.engine.portfolio_simulator.portfolio
            result.metrics = self.engine.performance_engine.evaluate(result)
            result.equity_curve = self.engine.portfolio_simulator.equity_curve or [("start", initial_cash)]
            result.drawdown_curve = self.engine.performance_engine.build_drawdown_curve(result.equity_curve)
        else:
            result = self.engine.run_backtest(
                symbols=validation["loaded_symbols"],
                market_data=validation["loaded_market_data"],
                interval=current_interval,
                period=period,
                progress_callback=progress_callback,
            )

            result.requested_symbols = requested_symbols
            result.loaded_symbols = validation["loaded_symbols"]
            result.failed_symbols = validation["failed_symbols"]
            result.completion_status = "success" if not validation["failed_symbols"] else "partial_success"

        self._finalize_result(
            result,
            initial_cash=initial_cash,
            commission_rate=commission_rate,
            spread=spread,
            slippage=slippage,
        )
        result.portfolio.metadata.update(
            {
                "strategy_id": strategy_id,
                "strategy_name": strategy_metadata["name"],
                "strategy_asset_class": strategy_metadata["asset_class"],
                "strategy_primary_timeframe": strategy_metadata["primary_timeframe"],
                "strategy_supported_timeframes": strategy_metadata["supported_timeframes"],
                "current_timeframe": current_interval,
                "timeframe_override": requested_interval is not None,
                "strategy_parameters": strategy_parameters,
            }
        )

        if self.container is not None:
            self.container.register_singleton("backtest_result", result)
            self.container.register_singleton("backtest_engine", self.engine)

        return result

    def run_strategy_comparison(
        self,
        configuration: dict[str, Any] | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ):
        config = configuration or {}

        initial_cash = self._parse_currency(config.get("capital"), default=100000.0)
        commission_rate = self._parse_rate(config.get("commission"), default=0.0005)
        spread = self._parse_float(config.get("spread"), default=0.02)
        slippage = self._parse_float(config.get("slippage"), default=0.01)
        period = self._period_from_date_range(config.get("date_range"), default="180d")
        requested_symbols = self._parse_symbols(config.get("symbols")) or self._default_symbols()
        strategy_ids = self._parse_strategy_ids(config.get("strategy_ids") or config.get("comparison_strategy_ids"))

        result = self.comparison_engine.compare(
            strategy_ids=strategy_ids,
            market_data={},
            symbols=requested_symbols,
            initial_cash=initial_cash,
            commission_rate=commission_rate,
            spread=spread,
            slippage=slippage,
            period=period,
            progress_callback=progress_callback,
        )

        if self.container is not None:
            self.container.register_singleton("comparison_result", result)

        return result

    def _resolve_engine(self) -> BacktestEngine:
        if self.container is not None and self.container.contains("backtest_engine"):
            engine = self.container.resolve("backtest_engine")
            if isinstance(engine, BacktestEngine):
                return engine

        strategy_engine = self._resolve("strategy_engine")
        risk_engine = self._resolve("risk_engine")
        data_engine = self._resolve("data_engine")
        scanner = self._resolve("scanner")
        engine = BacktestEngine(
            strategy_engine=strategy_engine,
            risk_engine=risk_engine,
            data_engine=data_engine,
            scanner=scanner,
        )
        if self.container is not None:
            self.container.register_singleton("backtest_engine", engine)
        return engine

    def get_strategy_definitions(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.strategy_registry.list_definitions()]

    def _resolve(self, name: str) -> Any:
        if self.container is None or not self.container.contains(name):
            return None
        return self.container.resolve(name)

    def _resolve_logger(self) -> Any:
        if self.container is not None and self.container.contains("logger"):
            return self.container.resolve("logger")
        return logging.getLogger(__name__)

    def _configure_engine(self, *, initial_cash: float, commission_rate: float, spread: float, slippage: float) -> None:
        self.engine.trade_simulator.commission_rate = max(0.0, float(commission_rate))
        self.engine.trade_simulator.bid_ask_spread = max(0.0, float(spread))
        self.engine.trade_simulator.slippage = max(0.0, float(slippage))

        self.engine.portfolio_simulator = PortfolioSimulator(initial_cash=initial_cash)
        self.engine.portfolio_simulator.portfolio.metadata.update(
            {
                "initial_cash": initial_cash,
                "commission_rate": commission_rate,
                "bid_ask_spread": spread,
                "slippage": slippage,
            }
        )

    def _configure_strategy(self, *, strategy_id: str, strategy_parameters: dict[str, Any]) -> Any:
        strategy = self.strategy_registry.create(strategy_id, strategy_parameters)
        self.engine.strategy_engine = StrategyLibraryEngine(strategy)
        return strategy

    def _finalize_result(
        self,
        result: BacktestResult,
        *,
        initial_cash: float,
        commission_rate: float,
        spread: float,
        slippage: float,
    ) -> None:
        result.initial_cash = initial_cash
        result.portfolio.metadata.update(
            {
                "initial_cash": initial_cash,
                "commission_rate": commission_rate,
                "bid_ask_spread": spread,
                "slippage": slippage,
            }
        )
        if result.completion_status == "pending":
            result.completion_status = "success" if not result.failed_symbols else "partial_success"
        if result.failed_symbols and result.completion_status == "success":
            result.completion_status = "partial_success"
        if not result.loaded_symbols and result.completion_status != "failed":
            result.completion_status = "failed"

    def _load_market_data(self, symbols: list[str], *, interval: str, period: str) -> dict[str, Any]:
        loaded_market_data: dict[str, Any] = {}
        loaded_symbols: list[str] = []
        failed_symbols: dict[str, str] = {}

        data_engine = self._resolve("data_engine") or getattr(self.engine, "data_engine", None)
        if data_engine is None or not hasattr(data_engine, "download_data"):
            reason = "Data engine unavailable"
            for symbol in symbols:
                failed_symbols[symbol] = reason
            self._log_failure(symbols, reason)
            return {
                "loaded_market_data": loaded_market_data,
                "loaded_symbols": loaded_symbols,
                "failed_symbols": failed_symbols,
            }

        for symbol in symbols:
            try:
                data = data_engine.download_data(symbol, interval=interval, period=period)
            except Exception as exc:  # pragma: no cover - defensive guard
                reason = str(exc)
                failed_symbols[symbol] = reason
                self._log_failure([symbol], reason)
                continue

            if data is None or getattr(data, "empty", False):
                reason = "No historical data returned"
                failed_symbols[symbol] = reason
                self._log_failure([symbol], reason)
                continue

            loaded_market_data[symbol] = data
            loaded_symbols.append(symbol)

        return {
            "loaded_market_data": loaded_market_data,
            "loaded_symbols": loaded_symbols,
            "failed_symbols": failed_symbols,
        }

    def _strategy_metadata(self, strategy: Any) -> dict[str, Any]:
        primary_timeframe = str(getattr(strategy, "primary_timeframe", "")).strip()
        if not primary_timeframe:
            raise ValueError("Strategy metadata must include a primary_timeframe.")

        return {
            "strategy_id": str(getattr(strategy, "strategy_id", "")),
            "name": str(getattr(strategy, "name", "")),
            "asset_class": str(getattr(strategy, "asset_class", "")),
            "primary_timeframe": primary_timeframe,
            "supported_timeframes": list(getattr(strategy, "supported_timeframes", []) or []),
        }

    def _parse_timeframe(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _default_symbols(self) -> list[str]:
        scanner = self._resolve("scanner")
        if scanner is not None and hasattr(scanner, "get_watchlist"):
            symbols = list(scanner.get_watchlist() or [])
            if symbols:
                return [str(symbol).strip().upper() for symbol in symbols if str(symbol).strip()]
        return ["AAPL"]

    def _log_failure(self, symbols: list[str], reason: str) -> None:
        message = f"Backtest data load failed for {', '.join(symbols)}: {reason}"
        if hasattr(self.logger, "warning"):
            self.logger.warning(message)
        else:
            logging.getLogger(__name__).warning(message)

    def _parse_currency(self, value: Any, default: float) -> float:
        if value is None:
            return default
        cleaned = str(value).replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except Exception:
            return default

    def _parse_rate(self, value: Any, default: float) -> float:
        if value is None:
            return default
        raw = str(value).strip()
        has_percent = raw.endswith("%")
        cleaned = raw.replace("%", "").replace(",", "")
        try:
            number = float(cleaned)
        except Exception:
            return default

        if has_percent:
            return max(0.0, number / 100.0)
        if number <= 0.01:
            return max(0.0, number)
        return max(0.0, number / 100.0)

    def _parse_float(self, value: Any, default: float) -> float:
        if value is None:
            return default
        cleaned = str(value).replace(",", "").strip()
        try:
            return float(cleaned)
        except Exception:
            return default

    def _parse_symbols(self, value: Any) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, list):
            symbols = [str(item).strip().upper() for item in value if str(item).strip()]
            return symbols or None
        if isinstance(value, str):
            symbols = [part.strip().upper() for part in value.split(",") if part.strip()]
            return symbols or None
        return None

    def _period_from_date_range(self, value: Any, default: str) -> str:
        if value is None:
            return default

        text = str(value).strip()
        if not text:
            return default

        delimiter = " to " if " to " in text else "->" if "->" in text else None
        if delimiter is None:
            return default

        parts = [part.strip() for part in text.split(delimiter)]
        if len(parts) != 2:
            return default

        try:
            start = datetime.fromisoformat(parts[0])
            end = datetime.fromisoformat(parts[1])
        except Exception:
            return default

        days = max(30, min(3650, (end - start).days + 1))
        return f"{days}d"

    def _parse_strategy_id(self, value: Any) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            return self.strategy_registry.default_strategy_id
        definition = self.strategy_registry.get_definition(text)
        if definition is None:
            return self.strategy_registry.default_strategy_id
        return definition.strategy_id

    def _parse_strategy_parameters(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        return dict(value)

    def _parse_strategy_ids(self, value: Any) -> list[str]:
        if isinstance(value, list):
            parsed = [self._parse_strategy_id(item) for item in value]
            return [item for item in parsed if item]
        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",")]
            return [part for part in parts if part]
        return []
