"""Trade History workspace page for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any

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
                "history": [],
                "statistics": {},
                "performance": {},
                "filters": {},
                "trades": [],
                "selected_trade": {},
                "events": [],
            }

        summary = self._coerce_mapping(self.data.get("summary", {}))
        history = self.data.get("history", self.data.get("trades", []))
        statistics = self._coerce_mapping(self.data.get("statistics", {}))
        performance = self._coerce_mapping(self.data.get("performance", statistics))
        if not isinstance(history, list):
            history = list(history or [])
        trades = self.data.get("trades", [])
        selected_trade = self.data.get("selected_trade", {})
        filters = self.data.get("filters", {})
        events = self.data.get("events", [])

        render_desktop_layout()
        render_panel_header("Trade History Overview", status="live")
        self._render_kpi_row(summary)

        main_left, main_right = st.columns([0.66, 0.34], gap="small")
        with main_left:
            render_section("Trade Journal", lambda: self._render_trade_table(trades))
        with main_right:
            render_section("Filters", lambda: self._render_filters_table(filters))
            render_section("Statistics", lambda: self._render_statistics_table(statistics))

        bottom_left, bottom_right = st.columns([0.5, 0.5], gap="small")
        with bottom_left:
            render_section("Selected Trade", lambda: self._render_selected_trade_table(selected_trade))
        with bottom_right:
            render_section("Recent Trade Events", lambda: self._render_events_table(events))

        render_information_banner(
            "Trade History Notes",
            self._build_banner_message(summary, performance, filters, selected_trade, history, events),
        )

        return self._build_compatibility_text(selected_trade)

    def _render_kpi_row(self, summary: dict[str, Any]) -> None:
        items = [
            ("Total Trades", summary.get("total_trades", 0)),
            ("Open Trades", summary.get("open_trades", 0)),
            ("Closed Trades", summary.get("closed_trades", 0)),
            ("Win Rate", summary.get("win_rate", "0%")),
            ("Net Profit", summary.get("net_profit", "$0")),
            ("Average Win", summary.get("average_win", "$0")),
            ("Average Loss", summary.get("average_loss", "$0")),
            ("Profit Factor", summary.get("profit_factor", "0.00")),
            ("Largest Win", summary.get("largest_win", "$0")),
            ("Largest Loss", summary.get("largest_loss", "$0")),
        ]

        col_count = 5
        for start in range(0, len(items), col_count):
            columns = st.columns(col_count, gap="small")
            for column, (title, value) in zip(columns, items[start : start + col_count]):
                with column:
                    render_kpi_card(
                        title=title,
                        value=self._stringify(value),
                        footer_label="Summary",
                        footer_value="Trade History",
                    )

    def _render_trade_table(self, trades: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Trade ID": self._stringify(item.get("trade_id", "-")),
                "Symbol": self._stringify(item.get("symbol", "-")),
                "Company": self._stringify(item.get("company", "-")),
                "Direction": self._stringify(item.get("direction", "-")),
                "Quantity": self._stringify(item.get("quantity", "-")),
                "Entry Price": self._stringify(item.get("entry_price", "-")),
                "Exit Price": self._stringify(item.get("exit_price", "-")),
                "Entry Time": self._stringify(item.get("entry_time", "-")),
                "Exit Time": self._stringify(item.get("exit_time", "-")),
                "Duration": self._stringify(item.get("duration", "-")),
                "Gross P&L": self._stringify(item.get("gross_pnl", "-")),
                "Net P&L": self._stringify(item.get("net_pnl", "-")),
                "Status": self._stringify(item.get("status", "-")),
                "Strategy": self._stringify(item.get("strategy", "-")),
                "Exit Reason": self._stringify(item.get("exit_reason", "-")),
            }
            for item in trades
        ]
        render_table(
            rows=rows,
            columns=[
                "Trade ID",
                "Symbol",
                "Company",
                "Direction",
                "Quantity",
                "Entry Price",
                "Exit Price",
                "Entry Time",
                "Exit Time",
                "Duration",
                "Gross P&L",
                "Net P&L",
                "Status",
                "Strategy",
                "Exit Reason",
            ],
            numeric_columns=["Quantity", "Entry Price", "Exit Price", "Gross P&L", "Net P&L"],
        )

    def _render_filters_table(self, filters: dict[str, Any]) -> None:
        rows = [
            {"Filter": "Date Range", "Value": self._stringify(filters.get("date_range", "All"))},
            {"Filter": "Symbol", "Value": self._stringify(filters.get("symbol", "All"))},
            {"Filter": "Strategy", "Value": self._stringify(filters.get("strategy", "All"))},
            {"Filter": "Direction", "Value": self._stringify(filters.get("direction", "All"))},
            {"Filter": "Status", "Value": self._stringify(filters.get("status", "All"))},
            {"Filter": "P/L", "Value": self._stringify(filters.get("profit_loss", "All"))},
            {"Filter": "Account", "Value": self._stringify(filters.get("account", "All"))},
        ]
        render_table(rows=rows, columns=["Filter", "Value"])

    def _render_statistics_table(self, statistics: dict[str, Any]) -> None:
        rows = [{"Metric": self._stringify(name), "Value": self._stringify(value)} for name, value in statistics.items()]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_selected_trade_table(self, selected_trade: dict[str, Any]) -> None:
        rows = [
            {"Field": "Trade ID", "Value": self._stringify(selected_trade.get("trade_id", "N/A"))},
            {"Field": "Symbol", "Value": self._stringify(selected_trade.get("symbol", "N/A"))},
            {"Field": "Company", "Value": self._stringify(selected_trade.get("company", "N/A"))},
            {"Field": "Direction", "Value": self._stringify(selected_trade.get("direction", "N/A"))},
            {"Field": "Quantity", "Value": self._stringify(selected_trade.get("quantity", "N/A"))},
            {"Field": "Entry Price", "Value": self._stringify(selected_trade.get("entry_price", "N/A"))},
            {"Field": "Exit Price", "Value": self._stringify(selected_trade.get("exit_price", "N/A"))},
            {"Field": "Entry Time", "Value": self._stringify(selected_trade.get("entry_time", "N/A"))},
            {"Field": "Exit Time", "Value": self._stringify(selected_trade.get("exit_time", "N/A"))},
            {"Field": "Duration", "Value": self._stringify(selected_trade.get("duration", "N/A"))},
            {"Field": "Gross P&L", "Value": self._stringify(selected_trade.get("gross_pnl", "N/A"))},
            {"Field": "Net P&L", "Value": self._stringify(selected_trade.get("net_pnl", "N/A"))},
            {"Field": "Status", "Value": self._stringify(selected_trade.get("status", "N/A"))},
            {"Field": "Strategy", "Value": self._stringify(selected_trade.get("strategy", "N/A"))},
            {"Field": "Entry Reason", "Value": self._stringify(selected_trade.get("entry_reason", "N/A"))},
            {"Field": "Exit Reason", "Value": self._stringify(selected_trade.get("exit_reason", "N/A"))},
            {"Field": "Risk Assessment", "Value": self._stringify(selected_trade.get("risk_assessment", "N/A"))},
            {"Field": "Stop Loss", "Value": self._stringify(selected_trade.get("stop_loss", "N/A"))},
            {"Field": "Take Profit", "Value": self._stringify(selected_trade.get("take_profit", "N/A"))},
            {"Field": "Commission", "Value": self._stringify(selected_trade.get("commission", "N/A"))},
            {"Field": "Slippage", "Value": self._stringify(selected_trade.get("slippage", "N/A"))},
            {"Field": "Position Sizing", "Value": self._stringify(selected_trade.get("position_sizing", "N/A"))},
            {"Field": "Account", "Value": self._stringify(selected_trade.get("account", "N/A"))},
            {"Field": "Timeline", "Value": self._stringify(selected_trade.get("timeline", []))},
            {"Field": "Related Events", "Value": self._stringify(selected_trade.get("related_events", []))},
        ]
        render_table(rows=rows, columns=["Field", "Value"])

    def _render_events_table(self, events: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Event": self._stringify(item.get("name", "N/A")),
                "Trade ID": self._stringify(item.get("trade_id", "N/A")),
            }
            for item in events
        ]
        render_table(rows=rows, columns=["Event", "Trade ID"])

    def _build_banner_message(
        self,
        summary: dict[str, Any],
        performance: dict[str, Any],
        filters: dict[str, Any],
        selected_trade: dict[str, Any],
        history: list[dict[str, Any]],
        events: list[dict[str, Any]],
    ) -> str:
        selected_trade_id = self._stringify(selected_trade.get("trade_id", "N/A"))
        selected_symbol = self._stringify(selected_trade.get("symbol", "N/A"))
        selected_status = self._stringify(selected_trade.get("status", "N/A"))
        trade_count = self._stringify(summary.get("total_trades", len(history)))
        win_rate = self._stringify(summary.get("win_rate", performance.get("win_rate", "N/A")))
        filter_state = ", ".join(
            [
                self._stringify(filters.get("date_range", "All")),
                self._stringify(filters.get("symbol", "All")),
                self._stringify(filters.get("strategy", "All")),
                self._stringify(filters.get("direction", "All")),
                self._stringify(filters.get("status", "All")),
                self._stringify(filters.get("profit_loss", "All")),
                self._stringify(filters.get("account", "All")),
            ]
        )
        event_count = self._stringify(len(events))
        return (
            f"Selected trade {selected_trade_id} ({selected_symbol}) is {selected_status}. "
            f"Total trades: {trade_count}. Win rate: {win_rate}. "
            f"Filters: {filter_state}. Events: {event_count}."
        )

    def _build_compatibility_text(self, selected_trade: dict[str, Any]) -> str:
        trade_id = self._stringify(selected_trade.get("trade_id", "TH-1001"))
        return (
            f"TRADE HISTORY WORKSPACE Dashboard / Trade History Status Bar "
            f"Total Trades Open Trades Closed Trades Filters {trade_id} Trade Detail"
        )

    def _coerce_mapping(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if is_dataclass(value):
            return asdict(value)
        if hasattr(value, "__dict__"):
            return dict(vars(value))
        return {}

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        return str(value)

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
