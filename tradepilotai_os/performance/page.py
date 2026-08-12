"""Performance workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.layout import empty_state
from dashboard.layout import render_desktop_layout
from dashboard.layout import render_kpi_card
from dashboard.layout import render_panel_header
from dashboard.layout import render_section
from dashboard.layout import render_table
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.workspace.base import WorkspacePage

from .data_provider import PerformanceDataProvider


class PerformancePage(WorkspacePage):
    """Render the professional read-only performance dashboard."""

    def __init__(self, data_provider: PerformanceDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Performance", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        self.data = self.data_provider.get_performance_dashboard_data() if self.data_provider is not None else {}

        render_desktop_layout()
        render_panel_header("Professional Performance Dashboard", status="read-only")

        render_section("Portfolio Overview", lambda: self._render_portfolio_overview(self.data.get("portfolio_overview", {})))
        render_section("Performance KPIs", lambda: self._render_performance_kpis(self.data.get("performance_kpis", {})))
        render_section("Equity Curve", lambda: self._render_equity_curve(self.data.get("equity_curve", {})))
        render_section("Drawdown", lambda: self._render_drawdown(self.data.get("drawdown", {})))
        render_section("Trade Analysis", lambda: self._render_trade_analysis(self.data.get("trade_analysis", {})))
        render_section("Strategy Analysis", lambda: self._render_strategy_analysis(self.data.get("strategy_analysis", [])))
        render_section("Exit Analysis", lambda: self._render_exit_analysis(self.data.get("exit_analysis", [])))
        render_section("Risk Analysis", lambda: self._render_risk_analysis(self.data.get("risk_analysis", {})))
        render_section("Charts", lambda: self._render_charts(self.data.get("charts", {})))

        self._render_export_buttons()

        return "performance"

    def _render_portfolio_overview(self, overview: dict[str, Any]) -> None:
        rows = [{"Metric": key.replace("_", " ").title(), "Value": self._format_value(value)} for key, value in overview.items()]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_performance_kpis(self, kpis: dict[str, Any]) -> None:
        items = [(key.replace("_", " ").title(), self._format_value(value)) for key, value in kpis.items()]
        cols = 4
        for start in range(0, len(items), cols):
            row = st.columns(cols, gap="small")
            for col, (title, value) in zip(row, items[start : start + cols]):
                with col:
                    render_kpi_card(title=title, value=value, footer_label="Performance", footer_value="Analytics")

    def _render_equity_curve(self, equity_curve: dict[str, Any]) -> None:
        running = equity_curve.get("running_equity", [])
        frame = pd.DataFrame(running)
        if frame.empty:
            empty_state("No equity data available")
            return

        chart = (
            alt.Chart(frame)
            .mark_line(strokeWidth=2.5)
            .encode(
                x=alt.X("timestamp:N", title="Timestamp"),
                y=alt.Y("value:Q", title="Equity"),
                tooltip=[alt.Tooltip("timestamp:N", title="Timestamp"), alt.Tooltip("value:Q", title="Equity", format=",.2f")],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

        detail_rows = [
            {"Series": "Running Equity", "Points": len(equity_curve.get("running_equity", []))},
            {"Series": "Peak Equity", "Points": len(equity_curve.get("peak_equity", []))},
            {"Series": "Drawdown Overlay", "Points": len(equity_curve.get("drawdown_overlay", []))},
        ]
        render_table(rows=detail_rows, columns=["Series", "Points"])

    def _render_drawdown(self, drawdown: dict[str, Any]) -> None:
        rows = [{"Metric": key.replace("_", " ").title(), "Value": self._format_value(value)} for key, value in drawdown.items()]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_trade_analysis(self, analysis: dict[str, Any]) -> None:
        rows = [{"Metric": key.replace("_", " ").title(), "Value": self._format_value(value)} for key, value in analysis.items()]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_strategy_analysis(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            empty_state("No strategy analysis available")
            return
        render_table(
            rows=[
                {
                    "Rank": row.get("rank", ""),
                    "Strategy": row.get("strategy_name", ""),
                    "Trades": row.get("trades", 0),
                    "Win Rate": row.get("win_rate", 0.0),
                    "Profit Factor": row.get("profit_factor", 0.0),
                    "Net Profit": row.get("net_profit", 0.0),
                    "Expectancy": row.get("expectancy", 0.0),
                    "Max Drawdown": row.get("maximum_drawdown", 0.0),
                    "Avg Holding": row.get("average_holding_time", 0.0),
                    "Total Return": row.get("total_return", 0.0),
                }
                for row in rows
            ],
            columns=[
                "Rank",
                "Strategy",
                "Trades",
                "Win Rate",
                "Profit Factor",
                "Net Profit",
                "Expectancy",
                "Max Drawdown",
                "Avg Holding",
                "Total Return",
            ],
        )

    def _render_exit_analysis(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            empty_state("No exit analysis available")
            return
        render_table(
            rows=[
                {
                    "Exit Type": row.get("exit_reason", ""),
                    "Count": row.get("count", 0),
                    "Percentage": row.get("percentage", 0.0),
                    "Net Profit": row.get("net_profit", 0.0),
                }
                for row in rows
            ],
            columns=["Exit Type", "Count", "Percentage", "Net Profit"],
        )

    def _render_risk_analysis(self, risk: dict[str, Any]) -> None:
        rows = [{"Metric": key.replace("_", " ").title(), "Value": self._format_value(value)} for key, value in risk.items()]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_charts(self, charts: dict[str, Any]) -> None:
        if not charts:
            empty_state("No chart data available")
            return
        rows = [{"Chart": key.replace("_", " ").title(), "Points": len(value) if isinstance(value, list) else 0} for key, value in charts.items()]
        render_table(rows=rows, columns=["Chart", "Points"])

    def _render_export_buttons(self) -> None:
        if self.data_provider is None:
            return
        cols = st.columns(3, gap="small")
        for col, (title, fmt) in zip(cols, [("Export CSV", "csv"), ("Export Excel", "excel"), ("Export JSON", "json")]):
            with col:
                data, filename, mime = self.data_provider.export(format_name=fmt)
                st.download_button(title, data=data, file_name=filename, mime=mime, use_container_width=True, key=f"performance_export_{fmt}")

    def _format_value(self, value: Any) -> str:
        if isinstance(value, float):
            return f"{value:,.2f}"
        return str(value)
