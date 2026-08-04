"""Risk Dashboard workspace page for the TradePilotAI OS."""

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

from .data_provider import RiskDataProvider


class RiskDashboardPage(WorkspacePage):
    """Render the portfolio and trading risk dashboard workspace."""

    def __init__(self, data_provider: RiskDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Risk", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_risk_data()
        else:
            self.data = {"assessment": {}, "exposures": [], "positions": [], "rules": [], "violations": [], "timeline": [], "events": []}

        assessment = self.data.get("assessment", {})
        exposures = self.data.get("exposures", [])
        positions = self.data.get("positions", [])
        rules = self.data.get("rules", [])
        violations = self.data.get("violations", [])
        timeline = self.data.get("timeline", [])
        events = self.data.get("events", [])

        render_desktop_layout()
        render_panel_header("Risk Overview", status="live")
        self._render_kpi_row(assessment)

        main_left, main_right = st.columns([0.6, 0.4], gap="small")
        with main_left:
            render_section("Portfolio Exposure", lambda: self._render_exposure_table(exposures))
        with main_right:
            render_section("Risk Rules", lambda: self._render_rules_table(rules))

        bottom_left, bottom_right = st.columns([0.6, 0.4], gap="small")
        with bottom_left:
            render_section("Position Risk", lambda: self._render_positions_table(positions))
        with bottom_right:
            render_section("Risk Timeline", lambda: self._render_timeline_table(timeline))

        render_information_banner("Risk Events", self._events_message(violations, events))

        return "RISK DASHBOARD Dashboard / Risk Portfolio Risk Score Total Exposure Portfolio Exposure Risk Rules Risk Timeline"

    def _render_kpi_row(self, assessment: dict[str, Any]) -> None:
        items = [
            ("Portfolio Risk Score", self._stringify(assessment.get("portfolio_risk_score", 0)), "Label", "score"),
            ("Total Exposure", self._currency(assessment.get("total_exposure", 0)), "Label", "exposure"),
            ("Available Cash", self._currency(assessment.get("available_cash", 0)), "Label", "cash"),
            ("Buying Power", self._currency(assessment.get("buying_power", 0)), "Label", "buying power"),
            ("Largest Position", self._stringify(assessment.get("largest_position", "N/A")), "Label", "largest"),
            ("Daily Risk", self._currency(assessment.get("daily_risk", 0)), "Label", "daily"),
            ("Maximum Drawdown", self._stringify(assessment.get("max_drawdown", 0)), "Label", "drawdown"),
            ("Value at Risk", self._currency(assessment.get("value_at_risk", 0)), "Label", "var"),
            ("Open Positions", self._stringify(assessment.get("open_positions", 0)), "Label", "count"),
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

    def _render_exposure_table(self, exposures: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Label": self._stringify(item.get("label", "N/A")),
                "Value": self._stringify(item.get("value", "N/A")),
                "Category": self._stringify(item.get("category", "N/A")),
            }
            for item in exposures
        ]
        render_table(rows=rows, columns=["Label", "Value", "Category"])

    def _render_positions_table(self, positions: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Symbol": self._stringify(item.get("symbol", "N/A")),
                "Position Size": self._stringify(item.get("position_size", "N/A")),
                "Risk %": self._stringify(item.get("risk_percent", "N/A")),
                "Stop Distance": self._stringify(item.get("stop_distance", "N/A")),
                "Unrealised P&L": self._stringify(item.get("unrealised_pnl", "N/A")),
                "Exposure %": self._stringify(item.get("exposure_percent", "N/A")),
                "Risk Rating": self._stringify(item.get("risk_rating", "N/A")),
            }
            for item in positions
        ]
        render_table(
            rows=rows,
            columns=["Symbol", "Position Size", "Risk %", "Stop Distance", "Unrealised P&L", "Exposure %", "Risk Rating"],
        )

    def _render_rules_table(self, rules: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Name": self._stringify(item.get("name", "N/A")),
                "Current Value": self._stringify(item.get("current_value", "N/A")),
                "Configured Limit": self._stringify(item.get("configured_limit", "N/A")),
                "Status": self._stringify(item.get("status", "N/A")),
            }
            for item in rules
        ]
        render_table(rows=rows, columns=["Name", "Current Value", "Configured Limit", "Status"])

    def _render_timeline_table(self, timeline: list[Any]) -> None:
        rows = [
            {
                "Event": self._stringify(item),
            }
            for item in timeline
        ]
        render_table(rows=rows, columns=["Event"])

    def _events_message(self, violations: Iterable[dict[str, Any]], events: Iterable[dict[str, Any]]) -> str:
        violation_items = [
            f"{self._stringify(item.get('name', 'N/A'))}: {self._stringify(item.get('details', ''))}"
            for item in violations
        ]
        event_items = [
            f"{self._stringify(item.get('name', 'N/A'))}: {self._stringify(item.get('details', ''))}"
            for item in events
        ]

        violations_text = ", ".join(violation_items) if violation_items else "None"
        events_text = ", ".join(event_items) if event_items else "None"
        return f"Violations: {violations_text}\nRecent Events: {events_text}"

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
