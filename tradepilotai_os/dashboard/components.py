"""Reusable dashboard panel components for the TradePilotAI OS home screen."""

from __future__ import annotations

from typing import Any


class DashboardPanel:
    """Base structure for a reusable dashboard panel."""

    def __init__(self, title: str, body: list[str] | None = None) -> None:
        self.title = title
        self.body = body or []

    def render(self) -> str:
        """Render a panel using a consistent dark-theme layout."""

        lines = [f"[{self.title}]", *self.body]
        return "\n".join(lines)


class SystemStatusPanel(DashboardPanel):
    """Display system health and runtime status."""

    def __init__(self, status: dict[str, Any] | None = None) -> None:
        payload = status or {
            "mode": "PAPER",
            "status": "ONLINE",
            "heartbeat": "LIVE",
            "last_sync": "--",
        }
        body = [
            f"Mode      : {payload['mode']}",
            f"Status    : {payload['status']}",
            f"Heartbeat : {payload['heartbeat']}",
            f"Last Sync : {payload['last_sync']}",
        ]
        super().__init__(title="System Status", body=body)


class KpiCardPanel(DashboardPanel):
    """Display a row of KPI cards."""

    def __init__(self, metrics: dict[str, Any] | None = None) -> None:
        payload = metrics or {
            "Equity": "$100,000",
            "PnL": "+$0.00",
            "Win Rate": "0%",
            "Signals": "0",
        }
        body = [f"{key}: {value}" for key, value in payload.items()]
        super().__init__(title="KPI Overview", body=body)


class EquityCurvePanel(DashboardPanel):
    """Display a simplified equity curve preview."""

    def __init__(self, points: list[tuple[str, float]] | None = None) -> None:
        payload = points or [("T1", 100000.0), ("T2", 101200.0), ("T3", 100800.0)]
        body = [f"{label}: {value:,.2f}" for label, value in payload]
        super().__init__(title="Equity Curve", body=body)


class PipelineSummaryPanel(DashboardPanel):
    """Display staged pipeline execution data."""

    def __init__(self, summary: dict[str, Any] | None = None) -> None:
        payload = summary or {
            "symbols_scanned": 0,
            "signals_generated": 0,
            "orders_submitted": 0,
            "orders_executed": 0,
            "orders_rejected": 0,
        }
        body = [
            f"Symbols scanned : {payload.get('symbols_scanned', 0)}",
            f"Signals generated: {payload.get('signals_generated', 0)}",
            f"Orders submitted : {payload.get('orders_submitted', 0)}",
            f"Orders executed : {payload.get('orders_executed', 0)}",
            f"Orders rejected : {payload.get('orders_rejected', 0)}",
        ]
        super().__init__(title="Pipeline Summary", body=body)


class PortfolioSnapshotPanel(DashboardPanel):
    """Display an overview of the simulated portfolio."""

    def __init__(self, portfolio: dict[str, Any] | None = None) -> None:
        payload = portfolio or {
            "cash": "$100,000.00",
            "exposure": "$0.00",
            "positions": 0,
            "pnl": "$0.00",
        }
        body = [
            f"Cash      : {payload.get('cash', '$0.00')}",
            f"Exposure  : {payload.get('exposure', '$0.00')}",
            f"Positions : {payload.get('positions', 0)}",
            f"PnL       : {payload.get('pnl', '$0.00')}",
        ]
        super().__init__(title="Portfolio Snapshot", body=body)


class MarketScannerSummaryPanel(DashboardPanel):
    """Display market scan results."""

    def __init__(self, results: list[dict[str, Any]] | None = None) -> None:
        payload = results or [
            {"symbol": "AAPL", "signal": "BUY", "score": 0.82},
            {"symbol": "MSFT", "signal": "HOLD", "score": 0.41},
        ]
        body = [f"{item['symbol']}: {item['signal']} ({item['score']:.2f})" for item in payload]
        super().__init__(title="Market Scanner Summary", body=body)


class StrategyPerformancePanel(DashboardPanel):
    """Display simple strategy performance stats."""

    def __init__(self, stats: dict[str, Any] | None = None) -> None:
        payload = stats or {
            "win_rate": "0%",
            "avg_trade": "$0.00",
            "max_drawdown": "0%",
        }
        body = [
            f"Win Rate      : {payload.get('win_rate', '0%')}",
            f"Avg Trade     : {payload.get('avg_trade', '$0.00')}",
            f"Max Drawdown  : {payload.get('max_drawdown', '0%')}",
        ]
        super().__init__(title="Strategy Performance", body=body)


class RecentTradesPanel(DashboardPanel):
    """Display recent trades from the broker or pipeline."""

    def __init__(self, trades: list[dict[str, Any]] | None = None) -> None:
        payload = trades or [
            {"symbol": "AAPL", "side": "BUY", "price": 100.0},
            {"symbol": "MSFT", "side": "SELL", "price": 250.0},
        ]
        body = [f"{item['symbol']} {item['side']} @ {item['price']:.2f}" for item in payload]
        super().__init__(title="Recent Trades", body=body)


class SystemMessagesPanel(DashboardPanel):
    """Display recent system messages and warnings."""

    def __init__(self, messages: list[str] | None = None) -> None:
        payload = messages or [
            "Paper broker initialized",
            "Waiting for next market scan",
        ]
        body = payload
        super().__init__(title="System Messages", body=body)
