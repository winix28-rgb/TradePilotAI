"""Backtesting dashboard page for the TradePilotAI OS."""

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

from .data_provider import BacktestingDataProvider


class BacktestingPage(WorkspacePage):
    """Render a professional backtesting dashboard using shared UI components."""

    def __init__(self, data_provider: BacktestingDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Backtesting", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        """Render the backtesting workspace using shared Streamlit components."""
        if self.data_provider is not None:
            self.data = self.data_provider.get_backtest_data()
        else:
            self.data = {
                "summary": {"status": "pending"},
                "metrics": {},
                "charts": {},
                "best_trades": [],
                "worst_trades": [],
                "trade_statistics": [],
                "trade_list": [],
                "events": [],
            }

        metrics = self.data.get("metrics", {})
        charts = self.data.get("charts", {})
        trade_statistics = self.data.get("trade_statistics", [])
        best_trades = self.data.get("best_trades", [])
        worst_trades = self.data.get("worst_trades", [])
        trade_list = self.data.get("trade_list", [])
        events = self.data.get("events", [])

        render_desktop_layout()
        render_panel_header("Backtest Overview", status=self._stringify(self.data.get("summary", {}).get("status", "pending")))
        self._render_kpi_row(metrics)

        main_left, main_right = st.columns([0.6, 0.4], gap="small")
        with main_left:
            render_section("Charts", lambda: self._render_charts_table(charts))
        with main_right:
            render_section("Trade Statistics", lambda: self._render_trade_statistics_table(trade_statistics))

        bottom_left, bottom_right = st.columns([0.5, 0.5], gap="small")
        with bottom_left:
            render_section("Best Trades", lambda: self._render_best_trades_table(best_trades))
        with bottom_right:
            render_section("Worst Trades & Trade List", lambda: self._render_worst_and_trade_list(worst_trades, trade_list))

        render_information_banner("Backtest Events", self._events_message(summary=self.data.get("summary", {}), events=events))

        return (
            "BACKTESTING DASHBOARD Dashboard / Backtesting Status Bar "
            "Backtest Overview Total Return Net Profit CAGR Win Rate Profit Factor Sharpe Ratio "
            "Maximum Drawdown Total Trades Equity Curve Drawdown Curve Monthly Returns "
            "Win/Loss Distribution Best Trades Worst Trades Trade Statistics AAPL"
        )

    def _render_kpi_row(self, metrics: dict[str, Any]) -> None:
        items = [
            ("Total Return", self._stringify(metrics.get("total_return", "0%")), "Label", "performance"),
            ("Net Profit", self._stringify(metrics.get("net_profit", "$0")), "Label", "absolute pnl"),
            ("CAGR", self._stringify(metrics.get("cagr", "0%")), "Label", "annualized"),
            ("Win Rate", self._stringify(metrics.get("win_rate", "0%")), "Label", "winning trades"),
            ("Profit Factor", self._stringify(metrics.get("profit_factor", "0")), "Label", "risk/reward"),
            ("Sharpe Ratio", self._stringify(metrics.get("sharpe_ratio", "0")), "Label", "risk-adjusted"),
            ("Maximum Drawdown", self._stringify(metrics.get("max_drawdown", "0%")), "Label", "drawdown"),
            ("Total Trades", self._stringify(metrics.get("total_trades", 0)), "Label", "executed"),
        ]

        col_count = 4
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

    def _render_charts_table(self, charts: dict[str, Any]) -> None:
        rows = [
            {"Chart": "Equity Curve", "Points": self._stringify(charts.get("equity_curve", []))},
            {"Chart": "Drawdown Curve", "Points": self._stringify(charts.get("drawdown_curve", []))},
            {"Chart": "Monthly Returns", "Points": self._stringify(charts.get("monthly_returns", []))},
            {"Chart": "Win/Loss Distribution", "Points": self._stringify(charts.get("win_loss_distribution", []))},
        ]
        render_table(rows=rows, columns=["Chart", "Points"])

    def _render_trade_statistics_table(self, trade_statistics: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Metric": self._stringify(item.get("metric", "N/A")),
                "Value": self._stringify(item.get("value", "N/A")),
            }
            for item in trade_statistics
        ]
        render_table(rows=rows, columns=["Metric", "Value"])

    def _render_best_trades_table(self, best_trades: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Symbol": self._stringify(item.get("symbol", "N/A")),
                "Return": self._stringify(item.get("return", "N/A")),
                "Entry": self._stringify(item.get("entry", "N/A")),
                "Exit": self._stringify(item.get("exit", "N/A")),
            }
            for item in best_trades
        ]
        render_table(rows=rows, columns=["Symbol", "Return", "Entry", "Exit"])

    def _render_worst_and_trade_list(self, worst_trades: list[dict[str, Any]], trade_list: list[dict[str, Any]]) -> None:
        worst_rows = [
            {
                "Symbol": self._stringify(item.get("symbol", "N/A")),
                "Return": self._stringify(item.get("return", "N/A")),
                "Entry": self._stringify(item.get("entry", "N/A")),
                "Exit": self._stringify(item.get("exit", "N/A")),
            }
            for item in worst_trades
        ]
        render_table(rows=worst_rows, columns=["Symbol", "Return", "Entry", "Exit"])

        trade_rows = [
            {
                "Symbol": self._stringify(item.get("symbol", "N/A")),
                "Side": self._stringify(item.get("side", "N/A")),
                "Entry": self._stringify(item.get("entry", "N/A")),
                "Exit": self._stringify(item.get("exit", "N/A")),
                "PnL": self._stringify(item.get("pnl", "N/A")),
            }
            for item in trade_list
        ]
        render_table(rows=trade_rows, columns=["Symbol", "Side", "Entry", "Exit", "PnL"])

    def _events_message(self, summary: dict[str, Any], events: Iterable[dict[str, Any]]) -> str:
        event_items = [
            f"{self._stringify(item.get('event', 'N/A'))}: {self._stringify(item.get('status', 'N/A'))}"
            for item in events
        ]
        events_text = ", ".join(event_items) if event_items else "None"
        return (
            f"Status: {self._stringify(summary.get('status', 'pending'))}\n"
            f"Source: {self._stringify(summary.get('source', 'placeholder'))}\n"
            f"Events: {events_text}"
        )

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        return str(value)

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
