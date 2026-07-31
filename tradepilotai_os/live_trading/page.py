"""Live Trading workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import Card, SectionHeader, StatusBadge, StatusBar, Toolbar
from tradepilotai_os.workspace import WorkspacePage

from .components import LiveTradingKpiCard, OrderTable, OrderTicketCard, PositionTable, TimelineCard, ValidationCard
from .data_provider import LiveTradingDataProvider


class LiveTradingPage(WorkspacePage):
    """Render the professional live-trading workspace."""

    def __init__(self, data_provider: LiveTradingDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Live Trading", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_live_trading_data()
        else:
            self.data = {"account": {}, "orders": [], "positions": [], "validation": {}, "request": {}, "timeline": [], "events": []}

        account = self.data.get("account", {})
        orders = self.data.get("orders", [])
        positions = self.data.get("positions", [])
        validation = self.data.get("validation", {})
        request = self.data.get("request", {})
        timeline = self.data.get("timeline", [])
        events = self.data.get("events", [])

        lines = [
            "",
            "=" * 80,
            "LIVE TRADING WORKSPACE",
            "=" * 80,
            "",
            self.build_title("Order Management", "Paper and live broker workflows"),
            "",
            self.build_toolbar("Trading Controls", ["Submit", "Validate", "Refresh"]),
            "",
            self.build_breadcrumbs("live_trading", "Live Trading"),
            "",
            StatusBadge(label="Live Trading", status="live").render(),
            "",
            LiveTradingKpiCard(title="Account Value", value=f"${account.get('account_value', 0):,.0f}", subtitle="value").render(),
            LiveTradingKpiCard(title="Available Cash", value=f"${account.get('available_cash', 0):,.0f}", subtitle="cash").render(),
            LiveTradingKpiCard(title="Buying Power", value=f"${account.get('buying_power', 0):,.0f}", subtitle="power").render(),
            LiveTradingKpiCard(title="Open Orders", value=str(account.get("open_orders", 0)), subtitle="orders").render(),
            LiveTradingKpiCard(title="Open Positions", value=str(account.get("open_positions", 0)), subtitle="positions").render(),
            LiveTradingKpiCard(title="Today's P&L", value=f"${account.get('todays_pnl', 0):,.0f}", subtitle="pnl").render(),
            LiveTradingKpiCard(title="Margin Used", value=f"${account.get('margin_used', 0):,.0f}", subtitle="margin").render(),
            LiveTradingKpiCard(title="Margin Available", value=f"${account.get('margin_available', 0):,.0f}", subtitle="margin").render(),
            LiveTradingKpiCard(title="Broker Status", value=str(account.get("broker_status", "Connected")), subtitle="status").render(),
            "",
            OrderTicketCard(request=request).render(),
            "",
            ValidationCard(validations=validation).render(),
            "",
            OrderTable(rows=orders).render(),
            "",
            PositionTable(rows=positions).render(),
            "",
            TimelineCard(steps=timeline).render(),
            "",
            Card(title="Order Events", body=[f"{item['name']}: {item.get('details', '')}" for item in events]).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "live_trading"
        items = ["Dashboard", "Live Trading"]
        if current_route and current_route != "live_trading":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
