"""Service-backed data provider for the backtesting dashboard."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.backtesting.comparison import StrategyComparisonResult
from tradepilotai_os.backtesting.result import BacktestResult
from tradepilotai_os.core.container import Container

from .service import BacktestingService


PROGRESS_STAGES = [
    "Loading historical data...",
    "Generating signals...",
    "Executing trades...",
    "Calculating performance...",
    "Building report...",
    "Completed",
]


class BacktestingDataProvider:
    """Resolve backtest metrics from the container and runtime state."""

    def __init__(
        self,
        container: Container | None = None,
        state: dict[str, Any] | None = None,
        service: BacktestingService | None = None,
    ) -> None:
        self.container = container
        self.state = state or {}
        self.service = service or BacktestingService(container=container)

    def run_backtest(self, configuration: dict[str, Any]) -> BacktestResult | None:
        self._reset_progress()
        requested_symbols = self._requested_symbols_from_configuration(configuration)
        self.state["backtest_requested_symbols"] = requested_symbols

        def progress(stage: str) -> None:
            self._mark_progress(stage)

        try:
            result = self.service.run_backtest(configuration=configuration, progress_callback=progress)
        except Exception as exc:
            self.state["backtest_error"] = str(exc)
            self.state["backtest_status"] = "failed"
            self.state["backtest_loaded_symbols"] = []
            self.state["backtest_failed_symbols"] = {symbol: str(exc) for symbol in requested_symbols}
            return None

        self.state["backtest_result"] = result
        self.state["backtest_status"] = "completed"
        self.state["backtest_loaded_symbols"] = list(result.loaded_symbols)
        self.state["backtest_failed_symbols"] = dict(result.failed_symbols)
        self._mark_progress("Completed")
        return result

    def run_strategy_comparison(self, configuration: dict[str, Any]) -> StrategyComparisonResult | None:
        self.state["comparison_status"] = "running"
        self.state.pop("comparison_error", None)

        requested_symbols = self._requested_symbols_from_configuration(configuration)
        self.state["comparison_requested_symbols"] = requested_symbols

        try:
            result = self.service.run_strategy_comparison(configuration=configuration)
        except Exception as exc:
            self.state["comparison_error"] = str(exc)
            self.state["comparison_status"] = "failed"
            self.state["comparison_loaded_symbols"] = []
            self.state["comparison_failed_symbols"] = {symbol: str(exc) for symbol in requested_symbols}
            return None

        self.state["comparison_result"] = result
        self.state["comparison_status"] = "completed"
        self.state["comparison_loaded_symbols"] = list(result.loaded_symbols)
        self.state["comparison_failed_symbols"] = dict(result.failed_symbols)
        return result

    def get_backtest_data(self) -> dict[str, Any]:
        result = self._resolve_backtest_result()
        if result is None:
            empty = self._empty_payload()
            empty["progress"] = self._progress_payload()
            empty["backtest_status"] = self._status_payload()
            return empty

        payload = result.to_dict()
        metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}
        monthly_returns = self._monthly_returns_from_equity_curve(result.equity_curve)
        summary = payload.get("summary", {"status": "completed", "source": "backtest_result"})
        if self.state.get("backtest_status") == "completed":
            summary = dict(summary)
            summary["status"] = "completed"

        return {
            "summary": summary,
            "configuration": self._configuration_from_result(result),
            "metrics": metrics,
            "charts": {
                "equity_curve": payload.get("equity_curve", []),
                "drawdown_curve": payload.get("drawdown_series", payload.get("drawdown_curve", [])),
                "monthly_returns": monthly_returns,
                "distribution": payload.get("distribution", []),
            },
            "performance_breakdown": {
                "monthly_returns": monthly_returns,
                "exit_reasons": metrics.get("exit_reason_breakdown", {}),
                "long_vs_short": {
                    "Long Trades": metrics.get("long_trades", 0),
                    "Short Trades": metrics.get("short_trades", 0),
                    "Long Win Rate": metrics.get("long_win_rate", 0),
                    "Short Win Rate": metrics.get("short_win_rate", 0),
                },
                "distribution": payload.get("distribution", []),
            },
            "trade_history": payload.get("closed_trades", []),
            "signal_explainability": payload.get("signals", []),
            "events": payload.get("events", []),
            "progress": self._progress_payload(),
            "backtest_status": self._status_payload(result),
            "comparison": self._comparison_payload(),
        }

    def get_comparison_data(self) -> dict[str, Any]:
        comparison = self._resolve_comparison_result()
        if comparison is None:
            return self._empty_comparison_payload()
        return comparison.to_dict()

    def _resolve(self, name: str) -> Any:
        if self.container is None or not self.container.contains(name):
            return None
        return self.container.resolve(name)

    def _empty_payload(self) -> dict[str, Any]:
        status = self.state.get("backtest_status", "pending")
        return {
            "summary": {"status": status, "source": "backtest_result"},
            "configuration": {},
            "metrics": {},
            "charts": {},
            "performance_breakdown": {},
            "trade_history": [],
            "signal_explainability": [],
            "events": [],
            "comparison": self._comparison_payload(),
        }

    def _empty_comparison_payload(self) -> dict[str, Any]:
        status = self.state.get("comparison_status", "pending")
        return {
            "summary": {"status": status, "source": "strategy_comparison", "strategy_count": 0},
            "configuration": {},
            "strategies": [],
            "table": [],
            "charts": {
                "equity_curve": [],
                "drawdown_curve": [],
                "monthly_returns": [],
                "trade_counts": [],
            },
        }

    def _resolve_backtest_result(self) -> BacktestResult | None:
        direct_state = self.state.get("backtest_result")
        if isinstance(direct_state, BacktestResult):
            return direct_state

        direct_container = self._resolve("backtest_result")
        if isinstance(direct_container, BacktestResult):
            return direct_container

        return None

    def _resolve_comparison_result(self) -> StrategyComparisonResult | None:
        direct_state = self.state.get("comparison_result")
        if isinstance(direct_state, StrategyComparisonResult):
            return direct_state

        direct_container = self._resolve("comparison_result")
        if isinstance(direct_container, StrategyComparisonResult):
            return direct_container

        return None

    def _configuration_from_result(self, result: BacktestResult) -> dict[str, Any]:
        metadata = dict(result.portfolio.metadata)
        commission = metadata.get("commission_rate", metadata.get("commission", "N/A"))
        spread = metadata.get("bid_ask_spread", metadata.get("spread", "N/A"))
        slippage = metadata.get("slippage", "N/A")
        strategy_id = metadata.get("strategy_id", "rsi_mean_reversion")
        strategy_name = metadata.get("strategy_name", "N/A")
        strategy_asset_class = metadata.get("strategy_asset_class", "N/A")
        strategy_primary_timeframe = metadata.get("strategy_primary_timeframe", "N/A")
        strategy_supported_timeframes = metadata.get("strategy_supported_timeframes", [])
        current_timeframe = metadata.get("current_timeframe", strategy_primary_timeframe)
        strategy_parameters = metadata.get("strategy_parameters", {})
        date_range = "N/A"
        if result.equity_curve:
            first = result.equity_curve[0][0]
            last = result.equity_curve[-1][0]
            date_range = f"{first} -> {last}"
        return {
            "date_range": date_range,
            "capital": result.initial_cash,
            "commission": commission,
            "spread": spread,
            "slippage": slippage,
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "strategy_asset_class": strategy_asset_class,
            "strategy_primary_timeframe": strategy_primary_timeframe,
            "strategy_supported_timeframes": list(strategy_supported_timeframes or []),
            "current_timeframe": current_timeframe,
            "strategy_parameters": strategy_parameters,
        }

    def _reset_progress(self) -> None:
        self.state["backtest_progress_stage"] = PROGRESS_STAGES[0]
        self.state["backtest_status"] = "running"
        self.state.pop("backtest_error", None)
        self.state["backtest_progress"] = {stage: "Pending" for stage in PROGRESS_STAGES}
        self.state["backtest_progress"][PROGRESS_STAGES[0]] = "Running"

    def _mark_progress(self, stage: str) -> None:
        current = self.state.get("backtest_progress", {item: "Pending" for item in PROGRESS_STAGES})
        if stage not in current:
            return

        for item in PROGRESS_STAGES:
            if item == stage:
                current[item] = "Running" if stage != "Completed" else "Completed"
                continue
            if PROGRESS_STAGES.index(item) < PROGRESS_STAGES.index(stage) and current[item] != "Completed":
                current[item] = "Completed"

        self.state["backtest_progress"] = current
        self.state["backtest_progress_stage"] = stage

    def _progress_payload(self) -> dict[str, Any]:
        progress = self.state.get("backtest_progress")
        if not isinstance(progress, dict):
            progress = {stage: "Pending" for stage in PROGRESS_STAGES}

        return {
            "current_stage": self.state.get("backtest_progress_stage", "Not started"),
            "stages": [{"stage": stage, "status": progress.get(stage, "Pending")} for stage in PROGRESS_STAGES],
            "error": self.state.get("backtest_error", ""),
        }

    def _status_payload(self, result: BacktestResult | None = None) -> dict[str, Any]:
        if result is not None:
            requested = list(result.requested_symbols)
            loaded = list(result.loaded_symbols)
            failed = dict(result.failed_symbols)
            completion_status = result.completion_status
        else:
            requested = list(self.state.get("backtest_requested_symbols", []))
            loaded = list(self.state.get("backtest_loaded_symbols", []))
            failed = dict(self.state.get("backtest_failed_symbols", {}))
            completion_status = self.state.get("backtest_status", "pending")

        return {
            "requested_symbols": requested,
            "loaded_symbols": loaded,
            "failed_symbols": failed,
            "completion_status": completion_status,
        }

    def _comparison_payload(self) -> dict[str, Any]:
        comparison = self._resolve_comparison_result()
        if comparison is None:
            return self._empty_comparison_payload()
        return comparison.to_dict()

    def _requested_symbols_from_configuration(self, configuration: dict[str, Any]) -> list[str]:
        symbols = self.service._parse_symbols(configuration.get("symbols")) if hasattr(self.service, "_parse_symbols") else None
        if symbols:
            return symbols
        return self.service._default_symbols() if hasattr(self.service, "_default_symbols") else []

    def _monthly_returns_from_equity_curve(self, points: list[tuple[Any, float]]) -> list[tuple[str, float]]:
        if not points:
            return []

        monthly: dict[str, list[float]] = {}
        for timestamp, value in points:
            month_key = self._month_key(timestamp)
            monthly.setdefault(month_key, []).append(float(value))

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
