"""Performance summary view rendering helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_performance(state: Any) -> None:
    """Render the performance summary view using the existing performance state."""
    performance = getattr(state, "performance", None)
    if performance is None:
        st.write("No performance data available.")
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

    cols = st.columns(2, gap="small")
    for index, (label, value) in enumerate(items):
        column = cols[index % 2]
        with column:
            st.caption(label)
            st.write(f"**{value}**")
            st.write("")


def _safe_value(obj: Any, attribute: str) -> str:
    if obj is None:
        return "N/A"
    value = getattr(obj, attribute, None)
    if value is None:
        return "N/A"
    return str(value)
