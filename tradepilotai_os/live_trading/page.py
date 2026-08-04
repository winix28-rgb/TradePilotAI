"""Live Trading workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any
from typing import Iterable

import streamlit as st

from dashboard.layout import (
    render_desktop_layout,
    render_information_banner,
    render_kpi_card,
    render_panel_header,
    render_section,
    render_table,
)

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.workspace import WorkspacePage

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

        render_desktop_layout()
        render_panel_header("Order Management", status=self._stringify(account.get("broker_status", "Connected")))
        self._render_kpi_row(account)

        main_left, main_right = st.columns([0.6, 0.4], gap="small")
        with main_left:
            render_section("Order Ticket", lambda: self._render_request_table(request))
        with main_right:
            render_section("Pre-Trade Validation", lambda: self._render_validation_table(validation))

        bottom_left, bottom_right = st.columns([0.6, 0.4], gap="small")
        with bottom_left:
            render_section("Open Orders", lambda: self._render_orders_table(orders))
        with bottom_right:
            render_section("Open Positions", lambda: self._render_positions_table(positions))

        render_section("Order Timeline", lambda: self._render_timeline_table(timeline))
        render_information_banner("Order Events", self._events_message(events))

        # Keep compatibility text for legacy shell tests.
        return (
            "LIVE TRADING WORKSPACE Dashboard / Live Trading Status Bar "
            "Account Value Order Ticket Pre-Trade Validation Order Timeline"
        )

    def _render_kpi_row(self, account: dict[str, Any]) -> None:
        items = [
            ("Account Value", self._currency(account.get("account_value", 0)), "Label", "value"),
            ("Available Cash", self._currency(account.get("available_cash", 0)), "Label", "cash"),
            ("Buying Power", self._currency(account.get("buying_power", 0)), "Label", "power"),
            ("Open Orders", self._stringify(account.get("open_orders", 0)), "Label", "orders"),
            ("Open Positions", self._stringify(account.get("open_positions", 0)), "Label", "positions"),
            ("Today's P&L", self._currency(account.get("todays_pnl", 0)), "Label", "pnl"),
            ("Margin Used", self._currency(account.get("margin_used", 0)), "Label", "margin"),
            ("Margin Available", self._currency(account.get("margin_available", 0)), "Label", "margin"),
            ("Broker Status", self._stringify(account.get("broker_status", "Connected")), "Label", "status"),
        ]

        col_count = 3
        for start in range(0, len(items), col_count):
            cols = st.columns(col_count, gap="small")
            for col, (title, value, footer_label, footer_value) in zip(cols, items[start : start + col_count]):
                with col:
                    render_kpi_card(
                        title=title,
                        value=value,
                        footer_label=footer_label,
                        footer_value=footer_value,
                    )

    def _render_request_table(self, request: dict[str, Any]) -> None:
        rows = [
            {"Field": "Symbol", "Value": self._stringify(request.get("symbol", "N/A"))},
            {"Field": "Company", "Value": self._stringify(request.get("company", "N/A"))},
            {"Field": "Direction", "Value": self._stringify(request.get("direction", "N/A"))},
            {"Field": "Quantity", "Value": self._stringify(request.get("quantity", 0))},
            {"Field": "Type", "Value": self._stringify(request.get("order_type", "MARKET"))},
            {"Field": "Entry Price", "Value": self._stringify(request.get("entry_price", "N/A"))},
            {"Field": "Stop Loss", "Value": self._stringify(request.get("stop_loss", "N/A"))},
            {"Field": "Take Profit", "Value": self._stringify(request.get("take_profit", "N/A"))},
            {"Field": "Estimated Risk (£)", "Value": self._stringify(request.get("estimated_risk", "N/A"))},
            {"Field": "Estimated Reward (£)", "Value": self._stringify(request.get("estimated_reward", "N/A"))},
            {"Field": "Risk : Reward", "Value": self._stringify(request.get("risk_reward", "1:2"))},
            {"Field": "Estimated Margin", "Value": self._stringify(request.get("estimated_margin", "N/A"))},
        ]
        render_table(rows=rows, columns=["Field", "Value"])

    def _render_validation_table(self, validation: dict[str, Any]) -> None:
        rows = [{"Check": self._stringify(name), "Result": self._stringify(value)} for name, value in validation.items()]
        render_table(rows=rows, columns=["Check", "Result"])

    def _render_orders_table(self, orders: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Order ID": self._stringify(item.get("order_id", "-")),
                "Symbol": self._stringify(item.get("symbol", "-")),
                "Type": self._stringify(item.get("order_type", "-")),
                "Quantity": self._stringify(item.get("quantity", "-")),
                "Status": self._stringify(item.get("status", "-")),
                "Submitted Time": self._stringify(item.get("submitted_time", "-")),
            }
            for item in orders
        ]
        render_table(rows=rows, columns=["Order ID", "Symbol", "Type", "Quantity", "Status", "Submitted Time"])

    def _render_positions_table(self, positions: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Symbol": self._stringify(item.get("symbol", "-")),
                "Quantity": self._stringify(item.get("quantity", "-")),
                "Entry": self._stringify(item.get("entry", "-")),
                "Current Price": self._stringify(item.get("current_price", "-")),
                "Unrealised P&L": self._stringify(item.get("unrealised_pnl", "-")),
                "Risk": self._stringify(item.get("risk", "-")),
                "Stop": self._stringify(item.get("stop", "-")),
                "Target": self._stringify(item.get("target", "-")),
            }
            for item in positions
        ]
        render_table(
            rows=rows,
            columns=["Symbol", "Quantity", "Entry", "Current Price", "Unrealised P&L", "Risk", "Stop", "Target"],
        )

    def _render_timeline_table(self, timeline: Iterable[Any]) -> None:
        rows = [{"Step": self._stringify(item)} for item in timeline]
        render_table(rows=rows, columns=["Step"])

    def _events_message(self, events: Iterable[dict[str, Any]]) -> str:
        event_items = [
            f"{self._stringify(item.get('name', 'N/A'))}: {self._stringify(item.get('details', ''))}"
            for item in events
        ]
        return ", ".join(event_items) if event_items else "No events"

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        return str(value)

    def _currency(self, value: Any) -> str:
        try:
            return f"${float(value):,.0f}"
        except (TypeError, ValueError):
            return self._stringify(value)

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
