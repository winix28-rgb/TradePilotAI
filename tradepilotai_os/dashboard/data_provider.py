"""Service-backed dashboard data provider for the TradePilotAI OS home screen."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container


class DashboardDataProvider:
    """Resolve dashboard data from the application container and runtime state."""

    def __init__(self, container: Container | None = None, app: Any | None = None, state: dict[str, Any] | None = None) -> None:
        self.container = container
        self.app = app
        self.state = state or {}

    def get_dashboard_data(self) -> dict[str, Any]:
        """Return a data payload for the dashboard page."""

        return {
            "system_status": self._get_system_status(),
            "kpis": self._get_kpis(),
            "equity_curve": self._get_equity_curve(),
            "pipeline_summary": self._get_pipeline_summary(),
            "portfolio_snapshot": self._get_portfolio_snapshot(),
            "scanner_summary": self._get_scanner_summary(),
            "strategy_performance": self._get_strategy_performance(),
            "recent_trades": self._get_recent_trades(),
            "system_messages": self._get_system_messages(),
        }

    def _resolve(self, name: str) -> Any:
        if self.container is None or not self.container.contains(name):
            return None
        return self.container.resolve(name)

    def _get_system_status(self) -> dict[str, Any]:
        data_engine = self._resolve("data_engine")
        broker = self._resolve("broker")
        config = self._resolve("config")

        mode = "PAPER" if broker is not None else "STANDBY"
        status = "ONLINE" if getattr(data_engine, "is_running", lambda: False)() else "STANDBY"
        heartbeat = "LIVE" if status == "ONLINE" else "IDLE"
        last_sync = getattr(data_engine, "last_sync", None)
        if last_sync is None:
            last_sync = "--"

        if config is not None and getattr(config, "get", None) is not None:
            strategy_conf = config.get("strategy", {}) if hasattr(config, "get") else {}
            if isinstance(strategy_conf, dict) and strategy_conf.get("timeframe"):
                last_sync = strategy_conf.get("timeframe")

        return {
            "mode": mode,
            "status": status,
            "heartbeat": heartbeat,
            "last_sync": str(last_sync),
        }

    def _get_kpis(self) -> dict[str, Any]:
        portfolio_snapshot = self._get_portfolio_snapshot()
        pipeline_summary = self._get_pipeline_summary()

        return {
            "Equity": portfolio_snapshot.get("equity", "$0.00"),
            "PnL": portfolio_snapshot.get("pnl", "$0.00"),
            "Win Rate": self._format_win_rate(pipeline_summary),
            "Signals": pipeline_summary.get("signals_generated", 0),
        }

    def _get_equity_curve(self) -> list[tuple[str, float]]:
        portfolio_manager = self._resolve("portfolio_manager")
        if portfolio_manager is not None and getattr(portfolio_manager, "state", None) is not None:
            state = portfolio_manager.state
            equity = getattr(state, "cash", 0.0) + getattr(state, "unrealised_pnl", 0.0)
            return [("Current", float(equity))]

        return []

    def _get_pipeline_summary(self) -> dict[str, Any]:
        if self.state.get("pipeline_summary") is not None:
            return self.state["pipeline_summary"]

        if getattr(self.app, "last_run_summary", None) is not None:
            return self.app.last_run_summary

        return {
            "symbols_scanned": 0,
            "signals_generated": 0,
            "orders_submitted": 0,
            "orders_executed": 0,
            "orders_rejected": 0,
        }

    def _get_portfolio_snapshot(self) -> dict[str, Any]:
        portfolio_manager = self._resolve("portfolio_manager")
        broker = self._resolve("broker")

        if portfolio_manager is not None and getattr(portfolio_manager, "state", None) is not None:
            state = portfolio_manager.state
            cash = getattr(state, "cash", 0.0)
            exposure = getattr(state, "exposure", 0.0)
            positions = len(getattr(state, "positions", {}) or {})
            pnl = getattr(state, "realised_pnl", 0.0) + getattr(state, "unrealised_pnl", 0.0)
            return {
                "cash": self._format_currency(cash),
                "exposure": self._format_currency(exposure),
                "positions": positions,
                "pnl": self._format_currency(pnl),
                "equity": self._format_currency(cash + pnl),
            }

        if broker is not None and getattr(broker, "portfolio", None) is not None:
            portfolio = broker.portfolio
            return {
                "cash": self._format_currency(getattr(portfolio, "cash", 0.0)),
                "exposure": self._format_currency(getattr(portfolio, "exposure", 0.0)),
                "positions": len(getattr(portfolio, "positions", {}) or {}),
                "pnl": self._format_currency(getattr(portfolio, "realised_pnl", 0.0)),
                "equity": self._format_currency(getattr(portfolio, "cash", 0.0)),
            }

        return {
            "cash": self._format_currency(0.0),
            "exposure": self._format_currency(0.0),
            "positions": 0,
            "pnl": self._format_currency(0.0),
            "equity": self._format_currency(0.0),
        }

    def _get_scanner_summary(self) -> list[dict[str, Any]]:
        scanner = self._resolve("scanner")
        watchlist = []
        if scanner is not None and hasattr(scanner, "get_watchlist"):
            try:
                watchlist = scanner.get_watchlist() or []
            except Exception:
                watchlist = []

        if not watchlist:
            watchlist = self.state.get("scanner_symbols", [])

        results = []
        for symbol in watchlist:
            results.append({"symbol": symbol, "signal": "UNKNOWN", "score": 0.0})
        return results

    def _get_strategy_performance(self) -> dict[str, Any]:
        pipeline_summary = self._get_pipeline_summary()
        return {
            "win_rate": self._format_win_rate(pipeline_summary),
            "avg_trade": "$0.00",
            "max_drawdown": "0%",
        }

    def _get_recent_trades(self) -> list[dict[str, Any]]:
        broker = self._resolve("broker")
        if broker is not None and getattr(broker, "executed_trades", None):
            trades = []
            for trade in broker.executed_trades:
                trades.append({
                    "symbol": getattr(trade, "ticker", "-"),
                    "side": getattr(trade, "direction", "-"),
                    "price": getattr(trade, "entry_price", 0.0),
                })
            return trades

        return []

    def _get_system_messages(self) -> list[str]:
        data_engine = self._resolve("data_engine")
        messages = []
        if data_engine is not None:
            messages.append(f"Data engine: {'running' if getattr(data_engine, 'is_running', lambda: False)() else 'idle'}")
        if self._get_pipeline_summary().get("signals_generated", 0) > 0:
            messages.append("Signals generated in latest run")
        if not messages:
            messages.append("No service data available")
        return messages

    def _format_currency(self, value: Any) -> str:
        try:
            return f"${float(value):,.2f}"
        except (TypeError, ValueError):
            return "$0.00"

    def _format_win_rate(self, pipeline_summary: dict[str, Any]) -> str:
        signals = pipeline_summary.get("signals_generated", 0)
        executed = pipeline_summary.get("orders_executed", 0)
        if signals <= 0:
            return "0%"
        return f"{(executed / signals * 100):.0f}%"
