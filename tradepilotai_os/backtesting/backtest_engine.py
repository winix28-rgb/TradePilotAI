"""Backtesting engine for the TradePilotAI OS."""

from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Callable
from typing import Any

try:  # pragma: no cover - pandas is available in the test environment, but keep the import optional.
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

from tradepilotai_os.core.data_engine import DataEngine
from tradepilotai_os.indicators.ema import EMA
from tradepilotai_os.indicators.rsi import RSI
from tradepilotai_os.scanner.market_scanner import MarketScanner
from tradepilotai_os.strategy.strategy_engine import StrategyEngine
from tradepilotai_os.risk.risk_engine import RiskEngine

from .performance_engine import PerformanceEngine
from .portfolio_simulator import PortfolioSimulator
from .result import BacktestResult
from .trade_simulator import OpenTradeState
from .trade_simulator import TradeSimulator


class BacktestEngine:
    """Run a modular backtest over historical market data.

    The engine consumes existing StrategyEngine signals without giving the
    strategy any knowledge that it is operating inside a backtest.
    """

    def __init__(
        self,
        strategy_engine: StrategyEngine | None = None,
        trade_simulator: TradeSimulator | None = None,
        portfolio_simulator: PortfolioSimulator | None = None,
        performance_engine: PerformanceEngine | None = None,
        data_engine: DataEngine | None = None,
        scanner: MarketScanner | None = None,
        risk_engine: RiskEngine | None = None,
        initial_cash: float = 100000.0,
        commission_rate: float = 0.0005,
        bid_ask_spread: float = 0.02,
        slippage: float = 0.01,
    ) -> None:
        self.strategy_engine = strategy_engine or StrategyEngine()
        self.risk_engine = risk_engine
        self.trade_simulator = trade_simulator or TradeSimulator(
            commission_rate=commission_rate,
            bid_ask_spread=bid_ask_spread,
            slippage=slippage,
            risk_engine=risk_engine,
        )
        self.portfolio_simulator = portfolio_simulator or PortfolioSimulator(initial_cash=initial_cash)
        self.performance_engine = performance_engine or PerformanceEngine()
        self.data_engine = data_engine or DataEngine()
        self.scanner = scanner or MarketScanner()

    def run(
        self,
        symbols: list[str] | None = None,
        market_data: dict[str, Any] | Any | None = None,
    ) -> dict[str, Any]:
        """Execute a backtest and return a dictionary for compatibility."""

        return self.run_backtest(symbols=symbols, market_data=market_data).to_dict()

    def run_backtest(
        self,
        symbols: list[str] | None = None,
        market_data: dict[str, Any] | Any | None = None,
        interval: str | None = None,
        period: str = "180d",
        progress_callback: Callable[[str], None] | None = None,
    ) -> BacktestResult:
        """Execute a backtest and return the structured result model."""

        self._emit_progress(progress_callback, "Loading historical data...")
        resolved_interval = self._resolve_interval(interval) if market_data is None else str(interval).strip() if interval is not None else ""
        datasets = self._resolve_datasets(symbols=symbols, market_data=market_data, interval=resolved_interval, period=period)
        result = BacktestResult(initial_cash=self.portfolio_simulator.initial_cash)
        result.portfolio.metadata.update(
            {
                "initial_cash": self.portfolio_simulator.initial_cash,
                "commission_rate": self.trade_simulator.commission_rate,
                "bid_ask_spread": self.trade_simulator.bid_ask_spread,
                "slippage": self.trade_simulator.slippage,
            }
        )

        self._emit_progress(progress_callback, "Generating signals...")
        self._emit_progress(progress_callback, "Executing trades...")

        for symbol, raw_data in datasets.items():
            prepared = self._prepare_market_data(raw_data)
            if prepared is None or len(prepared) < 30:
                result.symbol_results[symbol] = {
                    "status": "skipped",
                    "reason": "insufficient_data",
                }
                continue

            symbol_result = self._run_symbol_backtest(symbol, prepared, result)
            result.symbol_results[symbol] = symbol_result

        result.portfolio = self.portfolio_simulator.portfolio
        result.closed_trades = list(self.portfolio_simulator.closed_trades)
        result.open_trades = [state.trade for state in self.portfolio_simulator.open_trades.values()]
        result.trades = list(self.portfolio_simulator.closed_trades)
        self._emit_progress(progress_callback, "Calculating performance...")
        result.metrics = self.performance_engine.evaluate(result)
        result.equity_curve = self.portfolio_simulator.equity_curve or [("start", self.portfolio_simulator.initial_cash)]
        result.drawdown_curve = self.performance_engine.build_drawdown_curve(result.equity_curve)
        self._emit_progress(progress_callback, "Building report...")
        return result

    def _resolve_datasets(
        self,
        symbols: list[str] | None,
        market_data: dict[str, Any] | Any | None,
        interval: str,
        period: str,
    ) -> dict[str, Any]:
        if market_data is not None:
            if pd is not None and hasattr(market_data, "columns"):
                symbol = (symbols or ["MARKET"])[0]
                return {symbol: market_data}
            if isinstance(market_data, dict):
                return dict(market_data)
            symbol = (symbols or ["MARKET"])[0]
            return {symbol: market_data}

        watchlist = symbols or self.scanner.get_watchlist()
        datasets: dict[str, Any] = {}
        for symbol in watchlist:
            data = self.data_engine.download_data(symbol, interval=interval, period=period)
            if data is not None:
                datasets[symbol] = data
        return datasets

    def _resolve_interval(self, interval: str | None) -> str:
        if interval is not None and str(interval).strip():
            return str(interval).strip()

        strategy_engine = getattr(self.strategy_engine, "strategy", None)
        if strategy_engine is not None:
            strategy_interval = str(getattr(strategy_engine, "primary_timeframe", "")).strip()
            if strategy_interval:
                return strategy_interval

        strategy_interval = str(getattr(self.strategy_engine, "primary_timeframe", "")).strip()
        if strategy_interval:
            return strategy_interval

        raise ValueError("A strategy timeframe is required for historical data loading.")

    def _emit_progress(self, callback: Callable[[str], None] | None, message: str) -> None:
        if callback is None:
            return
        callback(message)

    def _prepare_market_data(self, market_data: Any) -> Any:
        if pd is None or not hasattr(market_data, "copy"):
            return market_data

        data = market_data.copy()
        if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:
            data.columns = data.columns.get_level_values(0)

        if "EMA12" not in data.columns:
            data["EMA12"] = EMA.calculate(data, 12)
        if "EMA26" not in data.columns:
            data["EMA26"] = EMA.calculate(data, 26)
        if "RSI" not in data.columns:
            data["RSI"] = RSI.calculate(data, 14)

        return data.dropna(subset=[column for column in ["Close", "EMA12", "EMA26", "RSI"] if column in data.columns])

    def _run_symbol_backtest(self, symbol: str, data: Any, result: BacktestResult) -> dict[str, Any]:
        active_trade: OpenTradeState | None = None
        last_close = None
        signal_count = 0

        for index in range(len(data)):
            history = data.iloc[: index + 1]
            if len(history) < 30:
                continue

            signal = self.strategy_engine.evaluate(symbol, history)
            result.signals.append(signal)
            signal_count += 1

            current_row = history.iloc[-1]
            timestamp = history.index[-1]
            current_close = float(current_row["Close"])
            last_close = current_close

            if active_trade is None:
                if signal.signal in {"BUY", "SELL"}:
                    trade_state = self.trade_simulator.open_trade(signal, timestamp)
                    if trade_state is None:
                        continue
                    self.portfolio_simulator.open_trade(trade_state)
                    active_trade = trade_state
                    self.portfolio_simulator.mark_to_market({symbol: current_close})
                continue

            exit = self.trade_simulator.resolve_exit(active_trade, current_row, signal)
            if exit is None:
                self.portfolio_simulator.mark_to_market({symbol: current_close})
                self.portfolio_simulator.record_equity_point(timestamp, current_close)
                continue

            closed_trade = self.portfolio_simulator.close_trade(active_trade, exit, timestamp)
            result.trades.append(closed_trade)
            active_trade = None
            self.portfolio_simulator.record_equity_point(timestamp, exit.exit_fill_price)

        if active_trade is not None and last_close is not None:
            final_timestamp = data.index[-1]
            exit = self.trade_simulator.build_exit(active_trade, last_close, "End of Test")
            closed_trade = self.portfolio_simulator.close_trade(active_trade, exit, final_timestamp)
            result.trades.append(closed_trade)
            self.portfolio_simulator.record_equity_point(final_timestamp, exit.exit_fill_price)

        return {
            "status": "completed",
            "signals": signal_count,
            "closed_trades": len(self.portfolio_simulator.closed_trades),
        }
