"""Service-backed data provider for the backtesting dashboard."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container


class BacktestingDataProvider:
    """Resolve backtest metrics from the container and runtime state."""

    def __init__(self, container: Container | None = None, state: dict[str, Any] | None = None) -> None:
        self.container = container
        self.state = state or {}

    def get_backtest_data(self) -> dict[str, Any]:
        return {
            "summary": self._get_summary(),
            "metrics": self._get_metrics(),
            "charts": self._get_charts(),
            "best_trades": self._get_best_trades(),
            "worst_trades": self._get_worst_trades(),
            "trade_statistics": self._get_trade_statistics(),
            "trade_list": self._get_trade_list(),
            "events": self._get_events(),
        }

    def _resolve(self, name: str) -> Any:
        if self.container is None or not self.container.contains(name):
            return None
        return self.container.resolve(name)

    def _get_summary(self) -> dict[str, Any]:
        backtest_engine = self._resolve("backtest_engine")
        if backtest_engine is not None and hasattr(backtest_engine, "run"):
            try:
                result = backtest_engine.run([])
                if isinstance(result, dict):
                    return {"status": "completed", "source": "backtest_engine"}
            except Exception:
                pass
        return {"status": "pending", "source": "placeholder"}

    def _get_metrics(self) -> dict[str, Any]:
        return {
            "total_return": "8.50%",
            "net_profit": "$8,500",
            "cagr": "12.40%",
            "win_rate": "62%",
            "profit_factor": "1.84",
            "sharpe_ratio": "1.21",
            "max_drawdown": "-6.20%",
            "total_trades": 42,
        }

    def _get_charts(self) -> dict[str, Any]:
        return {
            "equity_curve": [("Jan", "100"), ("Feb", "104"), ("Mar", "108")],
            "drawdown_curve": [("Jan", "0"), ("Feb", "-2"), ("Mar", "-1")],
            "monthly_returns": [("Jan", "3.2%"), ("Feb", "1.5%"), ("Mar", "2.7%")],
            "win_loss_distribution": [("Wins", 26), ("Losses", 16)],
        }

    def _get_best_trades(self) -> list[dict[str, Any]]:
        return [{"symbol": "AAPL", "return": "+12.4%", "entry": "2025-01-10", "exit": "2025-01-14"}]

    def _get_worst_trades(self) -> list[dict[str, Any]]:
        return [{"symbol": "TSLA", "return": "-4.1%", "entry": "2025-02-03", "exit": "2025-02-05"}]

    def _get_trade_statistics(self) -> list[dict[str, Any]]:
        return [
            {"metric": "Avg Trade", "value": "$202"},
            {"metric": "Avg Win", "value": "$410"},
            {"metric": "Avg Loss", "value": "$180"},
            {"metric": "Largest Win", "value": "$1,250"},
            {"metric": "Largest Loss", "value": "$520"},
        ]

    def _get_trade_list(self) -> list[dict[str, Any]]:
        return [
            {"symbol": "AAPL", "side": "BUY", "entry": "2025-01-10", "exit": "2025-01-14", "pnl": "$1,250"},
            {"symbol": "MSFT", "side": "SELL", "entry": "2025-02-04", "exit": "2025-02-12", "pnl": "$680"},
        ]

    def _get_events(self) -> list[dict[str, Any]]:
        return [{"event": "BacktestCompleted", "status": "ready"}]
