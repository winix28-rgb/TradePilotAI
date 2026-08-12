"""Strategy comparison engine for TradePilotAI backtests."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable

from .backtest_engine import BacktestEngine
from .performance_engine import PerformanceEngine
from .portfolio_simulator import PortfolioSimulator
from .result import BacktestResult
from .strategy_library import StrategyLibraryEngine
from .strategy_library import StrategyRegistry
from .trade_simulator import TradeSimulator


@dataclass(slots=True)
class StrategyComparisonRun:
    """Single strategy entry in a comparison run."""

    strategy_id: str
    strategy_name: str
    asset_class: str = ""
    primary_timeframe: str = ""
    supported_timeframes: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    equity_curve: list[tuple[Any, float]] = field(default_factory=list)
    drawdown_curve: list[tuple[Any, float]] = field(default_factory=list)
    monthly_returns: list[tuple[str, float]] = field(default_factory=list)
    requested_symbols: list[str] = field(default_factory=list)
    loaded_symbols: list[str] = field(default_factory=list)
    failed_symbols: dict[str, str] = field(default_factory=dict)
    completion_status: str = "pending"
    result: BacktestResult | None = None

    @property
    def total_trades(self) -> int:
        return int(self.metrics.get("total_trades", self.metrics.get("number_of_trades", 0)) or 0)

    @property
    def winning_trades(self) -> int:
        return int(self.metrics.get("winning_trades", 0) or 0)

    @property
    def losing_trades(self) -> int:
        return int(self.metrics.get("losing_trades", 0) or 0)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "asset_class": self.asset_class,
            "primary_timeframe": self.primary_timeframe,
            "supported_timeframes": list(self.supported_timeframes),
            "metrics": dict(self.metrics),
            "equity_curve": list(self.equity_curve),
            "drawdown_curve": list(self.drawdown_curve),
            "monthly_returns": list(self.monthly_returns),
            "requested_symbols": list(self.requested_symbols),
            "loaded_symbols": list(self.loaded_symbols),
            "failed_symbols": dict(self.failed_symbols),
            "completion_status": self.completion_status,
            "trade_count": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
        }
        if self.result is not None:
            payload["result"] = self.result.to_dict()
        return payload


@dataclass(slots=True)
class StrategyComparisonResult:
    """Structured output for multi-strategy backtest comparisons."""

    initial_cash: float = 0.0
    requested_symbols: list[str] = field(default_factory=list)
    loaded_symbols: list[str] = field(default_factory=list)
    failed_symbols: dict[str, str] = field(default_factory=dict)
    completion_status: str = "pending"
    comparison_runs: list[StrategyComparisonRun] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        runs = [run.to_dict() for run in self.comparison_runs]
        return {
            "summary": self._summary(),
            "configuration": self._configuration(),
            "strategies": runs,
            "table": [self._comparison_row(run) for run in self.comparison_runs],
            "charts": {
                "equity_curve": self._overlay_curve("equity_curve"),
                "drawdown_curve": self._overlay_curve("drawdown_curve"),
                "monthly_returns": self._overlay_monthly_returns(),
                "trade_counts": self._trade_counts(),
            },
        }

    def _summary(self) -> dict[str, Any]:
        return {
            "status": self.completion_status,
            "source": "strategy_comparison",
            "initial_cash": self.initial_cash,
            "strategy_count": len(self.comparison_runs),
        }

    def _configuration(self) -> dict[str, Any]:
        strategy_timeframes = {
            run.strategy_id: run.primary_timeframe
            for run in self.comparison_runs
            if run.primary_timeframe
        }
        unique_timeframes = sorted(set(strategy_timeframes.values()))
        return {
            "capital": self.initial_cash,
            "requested_symbols": list(self.requested_symbols),
            "loaded_symbols": list(self.loaded_symbols),
            "failed_symbols": dict(self.failed_symbols),
            "strategy_timeframes": strategy_timeframes,
            "recommended_timeframes": unique_timeframes,
            "timeframe_warning": len(unique_timeframes) > 1,
        }

    def _comparison_row(self, run: StrategyComparisonRun) -> dict[str, Any]:
        metrics = run.metrics
        return {
            "strategy_id": run.strategy_id,
            "strategy_name": run.strategy_name,
            "net_profit": metrics.get("net_profit", 0.0),
            "total_return": metrics.get("total_return", 0.0),
            "win_rate": metrics.get("win_rate", 0.0),
            "profit_factor": metrics.get("profit_factor", 0.0),
            "maximum_drawdown": metrics.get("maximum_drawdown", 0.0),
            "expectancy": metrics.get("expectancy", 0.0),
            "total_trades": run.total_trades,
            "winning_trades": run.winning_trades,
            "losing_trades": run.losing_trades,
            "completion_status": run.completion_status,
        }

    def _overlay_curve(self, attribute: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for run in self.comparison_runs:
            points = getattr(run, attribute, [])
            for timestamp, value in points:
                rows.append(
                    {
                        "strategy_id": run.strategy_id,
                        "strategy_name": run.strategy_name,
                        "timestamp": timestamp,
                        "value": float(value),
                    }
                )
        return rows

    def _overlay_monthly_returns(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for run in self.comparison_runs:
            for month, value in run.monthly_returns:
                rows.append(
                    {
                        "strategy_id": run.strategy_id,
                        "strategy_name": run.strategy_name,
                        "month": month,
                        "value": float(value),
                    }
                )
        return rows

    def _trade_counts(self) -> list[dict[str, Any]]:
        return [
            {
                "strategy_id": run.strategy_id,
                "strategy_name": run.strategy_name,
                "total_trades": run.total_trades,
                "winning_trades": run.winning_trades,
                "losing_trades": run.losing_trades,
            }
            for run in self.comparison_runs
        ]


class StrategyComparisonEngine:
    """Run several registered strategies against the same market data."""

    def __init__(
        self,
        *,
        strategy_registry: StrategyRegistry | None = None,
        performance_engine: PerformanceEngine | None = None,
        base_engine: BacktestEngine | None = None,
        engine_factory: Callable[[Any, float, float, float, float, Any, Any, Any], BacktestEngine] | None = None,
    ) -> None:
        self.strategy_registry = strategy_registry or StrategyRegistry()
        self.performance_engine = performance_engine or PerformanceEngine()
        self.base_engine = base_engine or BacktestEngine()
        self.engine_factory = engine_factory or self._default_engine_factory

    def compare(
        self,
        *,
        strategy_ids: list[str],
        market_data: dict[str, Any],
        symbols: list[str],
        initial_cash: float,
        commission_rate: float,
        spread: float,
        slippage: float,
        period: str = "180d",
        progress_callback: Callable[[str], None] | None = None,
    ) -> StrategyComparisonResult:
        comparison_runs: list[StrategyComparisonRun] = []
        data_engine = getattr(self.base_engine, "data_engine", None)

        for strategy_id in strategy_ids:
            strategy = self.strategy_registry.create(strategy_id)
            primary_timeframe = str(getattr(strategy, "primary_timeframe", "")).strip()
            if not primary_timeframe:
                raise ValueError(f"Strategy '{strategy_id}' does not declare a primary timeframe.")
            if progress_callback is not None:
                progress_callback(f"Loading {strategy.name} data ({primary_timeframe})...")

            strategy_market_data, loaded_symbols, failed_symbols = self._load_market_data_for_strategy(
                symbols=symbols,
                data_engine=data_engine,
                interval=primary_timeframe,
                period=period,
                progress_callback=progress_callback,
            )

            if progress_callback is not None:
                progress_callback(f"Comparing {strategy.name}...")

            engine = self.engine_factory(
                strategy,
                float(initial_cash),
                float(commission_rate),
                float(spread),
                float(slippage),
                getattr(self.base_engine, "data_engine", None),
                getattr(self.base_engine, "scanner", None),
                getattr(self.base_engine, "risk_engine", None),
            )
            result = engine.run_backtest(
                symbols=loaded_symbols,
                market_data=strategy_market_data,
                interval=primary_timeframe,
                period=period,
                progress_callback=None,
            )

            result.requested_symbols = list(symbols)
            result.loaded_symbols = list(loaded_symbols)
            result.failed_symbols = dict(failed_symbols)
            if failed_symbols and not loaded_symbols:
                result.completion_status = "failed"
            elif failed_symbols:
                result.completion_status = "partial_success"

            comparison_runs.append(
                StrategyComparisonRun(
                    strategy_id=strategy_id,
                    strategy_name=strategy.name,
                    asset_class=str(getattr(strategy, "asset_class", "")),
                    primary_timeframe=primary_timeframe,
                    supported_timeframes=list(getattr(strategy, "supported_timeframes", []) or []),
                    metrics=dict(result.metrics),
                    equity_curve=list(result.equity_curve),
                    drawdown_curve=list(result.drawdown_curve or result.drawdown_series),
                    monthly_returns=self._monthly_returns_from_equity_curve(result.equity_curve),
                    requested_symbols=list(result.requested_symbols),
                    loaded_symbols=list(result.loaded_symbols),
                    failed_symbols=dict(result.failed_symbols),
                    completion_status=result.completion_status,
                    result=result,
                )
            )

        return StrategyComparisonResult(
            initial_cash=initial_cash,
            requested_symbols=list(symbols),
            loaded_symbols=sorted({symbol for run in comparison_runs for symbol in run.loaded_symbols}),
            failed_symbols={symbol: reason for run in comparison_runs for symbol, reason in run.failed_symbols.items()},
            completion_status=self._comparison_status(comparison_runs),
            comparison_runs=comparison_runs,
        )

    def _load_market_data_for_strategy(
        self,
        *,
        symbols: list[str],
        data_engine: Any,
        interval: str,
        period: str,
        progress_callback: Callable[[str], None] | None = None,
    ) -> tuple[dict[str, Any], list[str], dict[str, str]]:
        loaded_market_data: dict[str, Any] = {}
        loaded_symbols: list[str] = []
        failed_symbols: dict[str, str] = {}

        if data_engine is None or not hasattr(data_engine, "download_data"):
            reason = "Data engine unavailable"
            for symbol in symbols:
                failed_symbols[symbol] = reason
            return loaded_market_data, loaded_symbols, failed_symbols

        for symbol in symbols:
            try:
                data = data_engine.download_data(symbol, interval=interval, period=period)
            except Exception as exc:  # pragma: no cover - defensive guard
                failed_symbols[symbol] = str(exc)
                continue

            if data is None or getattr(data, "empty", False):
                failed_symbols[symbol] = "No historical data returned"
                continue

            loaded_market_data[symbol] = data
            loaded_symbols.append(symbol)

        return loaded_market_data, loaded_symbols, failed_symbols

    def _default_engine_factory(
        self,
        strategy: Any,
        initial_cash: float,
        commission_rate: float,
        spread: float,
        slippage: float,
        data_engine: Any,
        scanner: Any,
        risk_engine: Any,
    ) -> BacktestEngine:
        trade_simulator = TradeSimulator(
            commission_rate=commission_rate,
            bid_ask_spread=spread,
            slippage=slippage,
            risk_engine=risk_engine,
        )
        return BacktestEngine(
            strategy_engine=StrategyLibraryEngine(strategy),
            trade_simulator=trade_simulator,
            portfolio_simulator=PortfolioSimulator(initial_cash=initial_cash),
            performance_engine=self.performance_engine,
            data_engine=data_engine,
            scanner=scanner,
            risk_engine=risk_engine,
        )

    def _comparison_status(self, runs: list[StrategyComparisonRun]) -> str:
        if not runs:
            return "failed"
        if any(run.completion_status != "success" for run in runs):
            return "partial_success"
        return "success"

    def _monthly_returns_from_equity_curve(self, points: list[tuple[Any, float]]) -> list[tuple[str, float]]:
        if not points:
            return []

        monthly: dict[str, list[float]] = {}
        for timestamp, value in points:
            monthly.setdefault(self._month_key(timestamp), []).append(float(value))

        rows: list[tuple[str, float]] = []
        for month in sorted(monthly.keys()):
            values = monthly[month]
            start_value = values[0]
            end_value = values[-1]
            if start_value == 0:
                change = 0.0
            else:
                change = ((end_value - start_value) / start_value) * 100.0
            rows.append((month, round(change, 2)))
        return rows

    def _month_key(self, timestamp: Any) -> str:
        text = str(timestamp)
        if len(text) >= 8 and text[4] == "-" and text[7] == "-":
            return text[:7]
        if " " in text and len(text.split(" ", 1)[0]) >= 7:
            token = text.split(" ", 1)[0]
            if len(token) >= 8 and token[4] == "-" and token[7] == "-":
                return token[:7]
        return text[:7] if len(text) >= 7 else text