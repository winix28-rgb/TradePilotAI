"""Performance summary view rendering helpers."""

from __future__ import annotations

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


def render_performance(state: Any) -> None:
    """Render the performance summary view using the existing performance state."""
    render_desktop_layout()
    render_panel_header("Performance Overview", status="live")

    performance = getattr(state, "performance", None)
    if performance is None:
        render_information_banner("Performance Notes", "No performance data available.")
        return

    items = [
        ("Trades", _safe_value(performance, "total_trades") or _safe_value(performance, "trades")),
        ("Wins", _safe_value(performance, "wins")),
        ("Losses", _safe_value(performance, "losses")),
        ("Win %", _safe_value(performance, "win_rate")),
        ("Profit Factor", _safe_value(performance, "profit_factor")),
        ("Average Win", _safe_value(performance, "average_win")),
        ("Average Loss", _safe_value(performance, "average_loss")),
    ]

    _render_kpi_row(items)

    render_section("Performance Metrics", lambda: _render_metrics_table(items))
    render_information_banner("Performance Notes", _build_performance_message(items))


def _render_kpi_row(items: list[tuple[str, str]]) -> None:
    col_count = 4
    for start in range(0, len(items), col_count):
        cols = st.columns(col_count, gap="small")
        for col, (label, value) in zip(cols, items[start : start + col_count]):
            with col:
                render_kpi_card(
                    title=label,
                    value=value,
                    footer_label="Metric",
                    footer_value="Performance",
                )


def _render_metrics_table(items: list[tuple[str, str]]) -> None:
    rows = [{"Metric": label, "Value": value} for label, value in items]
    render_table(rows=rows, columns=["Metric", "Value"])


def _build_performance_message(items: list[tuple[str, str]]) -> str:
    return "\n".join([f"{label}: {value}" for label, value in items])


def _safe_value(obj: Any, attribute: str) -> str:
    if obj is None:
        return "N/A"
    value = getattr(obj, attribute, None)
    if value is None:
        return "N/A"
    return str(value)
