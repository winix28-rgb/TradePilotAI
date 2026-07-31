"""Trade History workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import (
    Card,
    SectionHeader,
    StatusBadge,
    StatusBar,
    Toolbar,
)
from tradepilotai_os.workspace import WorkspacePage

from .components import TradeDetailCard, TradeFiltersCard, TradeHistoryKpiCard, TradeHistoryTable
from .data_provider import TradeHistoryDataProvider


class TradeHistoryPage(WorkspacePage):
    """Render the trade journal and audit trail workspace."""

    def __init__(self, data_provider: TradeHistoryDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Trade History", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_trade_history_data()
        else:
            self.data = {
                "summary": {},
                "statistics": {},
                "filters": {},
                "trades": [],
                "selected_trade": {},
                "events": [],
            }

        summary = self.data.get("summary", {})
        if hasattr(summary, "__dict__") and not isinstance(summary, dict):
            summary = {
                "total_trades": getattr(summary, "total_trades", 0),
                "open_trades": getattr(summary, "open_trades", 0),
                "closed_trades": getattr(summary, "closed_trades", 0),
                "win_rate": getattr(summary, "win_rate", "0%"),
                "net_profit": getattr(summary, "net_profit", "$0"),
                "average_win": getattr(summary, "average_win", "$0"),
                "average_loss": getattr(summary, "average_loss", "$0"),
                "profit_factor": getattr(summary, "profit_factor", "0.00"),
                "largest_win": getattr(summary, "largest_win", "$0"),
                "largest_loss": getattr(summary, "largest_loss", "$0"),
            }
        trades = self.data.get("trades", [])
        selected_trade = self.data.get("selected_trade", {})
        filters = self.data.get("filters", {})
        events = self.data.get("events", [])

        lines = [
            "",
            "=" * 80,
            "TRADE HISTORY WORKSPACE",
            "=" * 80,
            "",
            self.build_title("Trade Journal", "Professional audit trail"),
            "",
            self.build_toolbar("Trade History Controls", ["Filter", "Refresh", "Export"]),
            "",
            self.build_breadcrumbs("trade_history", "Trade History"),
            "",
            StatusBadge(label="Trade History", status="live").render(),
            "",
            TradeHistoryKpiCard(title="Total Trades", value=str(summary.get("total_trades", 0)), subtitle="records").render(),
            TradeHistoryKpiCard(title="Open Trades", value=str(summary.get("open_trades", 0)), subtitle="active").render(),
            TradeHistoryKpiCard(title="Closed Trades", value=str(summary.get("closed_trades", 0)), subtitle="completed").render(),
            TradeHistoryKpiCard(title="Win Rate", value=str(summary.get("win_rate", "0%")), subtitle="performance").render(),
            TradeHistoryKpiCard(title="Net Profit", value=str(summary.get("net_profit", "$0")), subtitle="pnl").render(),
            TradeHistoryKpiCard(title="Average Win", value=str(summary.get("average_win", "$0")), subtitle="wins").render(),
            TradeHistoryKpiCard(title="Average Loss", value=str(summary.get("average_loss", "$0")), subtitle="losses").render(),
            TradeHistoryKpiCard(title="Profit Factor", value=str(summary.get("profit_factor", "0.00")), subtitle="ratio").render(),
            TradeHistoryKpiCard(title="Largest Win", value=str(summary.get("largest_win", "$0")), subtitle="best trade").render(),
            TradeHistoryKpiCard(title="Largest Loss", value=str(summary.get("largest_loss", "$0")), subtitle="worst trade").render(),
            "",
            TradeFiltersCard(filters=filters).render(),
            "",
            TradeHistoryTable(rows=trades).render(),
            "",
            TradeDetailCard(trade=selected_trade).render(),
            "",
            Card(title="Recent Trade Events", body=[f"{item['name']}: {item['trade_id']}" for item in events]).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "trade_history"
        items = ["Dashboard", "Trade History"]
        if current_route and current_route != "trade_history":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
