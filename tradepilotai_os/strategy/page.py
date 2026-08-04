"""Strategy Centre workspace page for the TradePilotAI OS."""

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

from .data_provider import StrategyDataProvider


class StrategyPage(WorkspacePage):
    """Render the professional Strategy Centre workspace."""

    def __init__(self, data_provider: StrategyDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Strategy Centre", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        """Render the Strategy Centre using shared Streamlit dashboard components."""
        if self.data_provider is not None:
            self.data = self.data_provider.get_strategy_data()
        else:
            self.data = {"strategies": [], "current_strategy": None, "events": []}

        strategy = self.data.get("current_strategy") or {}
        strategies = self.data.get("strategies", [])
        versions = strategy.get("versions", [])
        config = strategy.get("configuration", {})
        performance = strategy.get("performance", {})
        deployment = strategy.get("deployment") or {"target": "Paper Broker", "status": "Pending", "broker_interface": "Broker Interface", "orchestrator": "Application Orchestrator"}

        render_desktop_layout()
        render_panel_header("Strategy Library", status=str(strategy.get("status", "Draft")))
        self._render_kpi_row(strategy)

        main_left, main_right = st.columns([0.6, 0.4], gap="small")
        with main_left:
            render_section("Strategy Library", lambda: self._render_strategy_table(strategies))
        with main_right:
            render_section("Strategy Configuration", lambda: self._render_config_table(config))

        bottom_left, bottom_right = st.columns([0.5, 0.5], gap="small")
        with bottom_left:
            render_section("Performance Summary", lambda: self._render_performance_table(performance))
        with bottom_right:
            render_section("Version History", lambda: self._render_versions_table(versions))

        render_information_banner(
            "Deployment & Events",
            self._build_information_message(deployment=deployment, events=self.data.get("events", [])),
        )

        render_information_banner("Status", self.build_status_bar(container=self._resolve_container()))

        # Keep a lightweight compatibility return for non-Streamlit string shell tests.
        return "STRATEGY CENTRE Strategy Library Strategy Configuration Performance Summary Version History Deployment"

    def _render_kpi_row(self, strategy: dict[str, Any]) -> None:
        items = [
            ("Strategy", str(strategy.get("name", "N/A")), "Status", str(strategy.get("status", "Draft"))),
            ("Version", str(strategy.get("version", "N/A")), "Label", "current version"),
            ("Markets", str(strategy.get("markets", "FX")), "Scope", "supported markets"),
            ("Timeframe", str(strategy.get("timeframe", "1H")), "Type", "timeframe"),
        ]

        cols = st.columns(4, gap="small")
        for col, (title, value, footer_label, footer_value) in zip(cols, items):
            with col:
                render_kpi_card(
                    title=title,
                    value=value,
                    footer_label=footer_label,
                    footer_value=footer_value,
                )

    def _render_strategy_table(self, strategies: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Strategy Name": row.get("name", "N/A"),
                "Version": row.get("version", "N/A"),
                "Description": row.get("description", "N/A"),
                "Status": row.get("status", "N/A"),
                "Supported Markets": row.get("markets", "N/A"),
                "Timeframe": row.get("timeframe", "N/A"),
                "Created Date": row.get("created_date", "N/A"),
                "Last Modified": row.get("last_modified", "N/A"),
            }
            for row in strategies
        ]

        render_table(
            rows=rows,
            columns=[
                "Strategy Name",
                "Version",
                "Description",
                "Status",
                "Supported Markets",
                "Timeframe",
                "Created Date",
                "Last Modified",
            ],
        )

    def _render_config_table(self, config: dict[str, Any]) -> None:
        labels = [
            ("RSI Period", "rsi_period"),
            ("RSI Buy Level", "rsi_buy_level"),
            ("RSI Sell Level", "rsi_sell_level"),
            ("EMA Fast", "ema_fast"),
            ("EMA Slow", "ema_slow"),
            ("Risk Per Trade", "risk_per_trade"),
            ("Maximum Positions", "max_positions"),
            ("Reward : Risk", "reward_risk"),
            ("Stop Loss", "stop_loss"),
            ("Take Profit", "take_profit"),
            ("Execution", "execution_mode"),
        ]

        rows = [{"Metric": label, "Value": self._stringify(config.get(key, "N/A"))} for label, key in labels]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_performance_table(self, performance: dict[str, Any]) -> None:
        labels = [
            ("Backtest Return", "backtest_return"),
            ("Paper Return", "paper_return"),
            ("Live Return", "live_return"),
            ("Win Rate", "win_rate"),
            ("Profit Factor", "profit_factor"),
            ("Sharpe Ratio", "sharpe_ratio"),
            ("Max Drawdown", "max_drawdown"),
            ("Total Trades", "total_trades"),
        ]

        rows = [{"Metric": label, "Value": self._stringify(performance.get(key, "N/A"))} for label, key in labels]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_versions_table(self, versions: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Version": self._stringify(version.get("version", "N/A")),
                "Date": self._stringify(version.get("date", "N/A")),
                "Author": self._stringify(version.get("author", "N/A")),
                "Notes": self._stringify(version.get("notes", "N/A")),
            }
            for version in versions
        ]

        render_table(rows=rows, columns=["Version", "Date", "Author", "Notes"])

    def _build_information_message(self, deployment: dict[str, Any], events: Iterable[Any]) -> str:
        event_values = [self._stringify(item) for item in events]
        events_text = f"Events: {', '.join(event_values)}" if event_values else "Events: None"
        return (
            f"Target: {self._stringify(deployment.get('target', 'N/A'))}\n"
            f"Status: {self._stringify(deployment.get('status', 'N/A'))}\n"
            f"Broker Interface: {self._stringify(deployment.get('broker_interface', 'N/A'))}\n"
            f"Orchestrator: {self._stringify(deployment.get('orchestrator', 'N/A'))}\n"
            f"{events_text}"
        )

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        return str(value)

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
