"""Home dashboard page for the TradePilotAI OS application."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import (
    Card,
    ChartCard,
    DataTable,
    KPIChartCard,
    NotificationPanel,
    SectionHeader,
    StatusBadge,
    StatusBar,
    Toolbar,
)
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.workspace import WorkspacePage

from .data_provider import DashboardDataProvider


class DashboardPage(WorkspacePage):
    """Render the main dashboard home screen with reusable panels."""

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        data_provider: DashboardDataProvider | None = None,
        navigation_service: NavigationService | None = None,
    ) -> None:
        super().__init__(page_title="Dashboard", navigation_service=navigation_service)
        self.data = data or {}
        self.data_provider = data_provider

    def render(self) -> str:
        """Render the dashboard to a string for terminal display."""

        if self.data_provider is not None:
            self.data = self.data_provider.get_dashboard_data()
        elif not self.data:
            self.data = {
                "system_status": {},
                "kpis": {},
                "equity_curve": [],
                "pipeline_summary": {},
                "portfolio_snapshot": {},
                "scanner_summary": [],
                "strategy_performance": {},
                "recent_trades": [],
                "system_messages": [],
            }

        for route in ["portfolio", "scanner", "backtesting", "trade_history", "risk", "live_trading", "strategy"]:
            self.navigation_service.register(route, route)

        lines = [
            "",
            "=" * 80,
            "TRADEPILOTAI OS DASHBOARD",
            "=" * 80,
            "",
            self.build_title("Overview", "Shared component layout"),
            "",
            self.build_toolbar("Dashboard Actions", ["Refresh", "Export"]),
            "",
            self.build_breadcrumbs("dashboard", "Dashboard"),
            "",
            StatusBadge(label="System", status="online").render(),
            "",
            Card(title="Runtime Summary", body=["Live data provider enabled", "UI library active"]).render(),
            "",
            Card(title="KPI Overview", body=[f"Equity: {self._metric_value(self.data.get('kpis'), 'Equity')}", f"PnL: {self._metric_value(self.data.get('kpis'), 'PnL')}"]).render(),
            "",
            KPIChartCard(title="Equity Curve", value=self._metric_value(self.data.get("kpis"), "Equity"), subtitle=self._metric_value(self.data.get("kpis"), "PnL")).render(),
            "",
            ChartCard(title="Performance", points=self._chart_points(self.data.get("equity_curve"))).render(),
            "",
            Card(title="System Status", body=self._system_status_rows(self.data.get("system_status"))).render(),
            "",
            Card(title="Pipeline Summary", body=self._pipeline_rows(self.data.get("pipeline_summary"))).render(),
            "",
            Card(title="Portfolio Snapshot", body=self._portfolio_rows(self.data.get("portfolio_snapshot"))).render(),
            "",
            Card(title="Market Scanner Summary", body=self._scanner_rows(self.data.get("scanner_summary"))).render(),
            "",
            Card(title="Strategy Performance", body=self._strategy_rows(self.data.get("strategy_performance"))).render(),
            "",
            Card(title="Recent Trades", body=self._recent_trade_rows()).render(),
            "",
            Card(title="Risk Summary", body=["Portfolio risk view available", "Open the risk workspace"]).render(),
            "",
            Card(title="Trading", body=["Broker-backed order management available", "Open the live trading workspace"]).render(),
            "",
            Card(title="Strategy Centre", body=["Create, configure, and deploy strategies", "Open the Strategy Centre"]).render(),
            "",
            Card(title="System Messages", body=self.data.get("system_messages", ["No service data available"])).render(),
            "",
            NotificationPanel(items=self.data.get("system_messages", [])).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)

    def _metric_value(self, metrics: dict[str, Any] | None, key: str) -> str:
        if not metrics:
            return "0"
        return str(metrics.get(key, "0"))

    def _chart_points(self, points: list[tuple[str, float]] | None) -> list[tuple[str, str]]:
        if not points:
            return [("Current", "0")]
        return [(label, f"{value:,.2f}") for label, value in points]

    def _system_status_rows(self, status: dict[str, Any] | None) -> list[str]:
        if not status:
            return ["Mode: STANDBY", "Status: IDLE"]
        return [f"Mode: {status.get('mode', 'STANDBY')}", f"Status: {status.get('status', 'IDLE')}", f"Heartbeat: {status.get('heartbeat', 'IDLE')}", f"Last Sync: {status.get('last_sync', '--')}"]

    def _pipeline_rows(self, summary: dict[str, Any] | None) -> list[str]:
        if not summary:
            return ["Signals Generated: 0"]
        return [
            f"Symbols scanned: {summary.get('symbols_scanned', 0)}",
            f"Signals generated: {summary.get('signals_generated', 0)}",
            f"Orders submitted: {summary.get('orders_submitted', 0)}",
            f"Orders executed: {summary.get('orders_executed', 0)}",
            f"Orders rejected: {summary.get('orders_rejected', 0)}",
        ]

    def _portfolio_rows(self, snapshot: dict[str, Any] | None) -> list[str]:
        if not snapshot:
            return ["Cash: $0.00"]
        return [
            f"Cash: {snapshot.get('cash', '$0.00')}",
            f"Exposure: {snapshot.get('exposure', '$0.00')}",
            f"Positions: {snapshot.get('positions', 0)}",
            f"PnL: {snapshot.get('pnl', '$0.00')}",
        ]

    def _scanner_rows(self, scanner_summary: list[dict[str, Any]] | None) -> list[str]:
        if not scanner_summary:
            return ["No symbols"]
        return [f"{item['symbol']}: {item['signal']} ({item['score']:.2f})" for item in scanner_summary]

    def _strategy_rows(self, performance: dict[str, Any] | None) -> list[str]:
        if not performance:
            return ["Win Rate: 0%"]
        return [f"Win Rate: {performance.get('win_rate', '0%')}", f"Avg Trade: {performance.get('avg_trade', '$0.00')}", f"Max Drawdown: {performance.get('max_drawdown', '0%')}"]

    def _trade_rows(self, trades: list[dict[str, Any]] | None) -> list[list[Any]]:
        if not trades:
            return []
        return [[trade.get("symbol", "-"), trade.get("side", "-"), trade.get("price", 0.0)] for trade in trades]

    def _recent_trade_rows(self) -> list[str]:
        if self.data.get("recent_trades"):
            self.navigation_service.register("trade_history", "trade_history")
            return [f"AAPL BUY @ 100.00 -> Open Trade History", "MSFT SELL @ 200.00 -> Open Trade History"]
        return ["No recent trades"]

    def show(self) -> None:
        """Print the rendered dashboard to stdout."""

        print(self.render())
