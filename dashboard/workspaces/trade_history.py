"""Trade history workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from tradepilotai_os.trade_history import TradeHistoryPage


def render_trade_history_workspace(state: Any) -> None:
    """Render the trade history workspace."""
    st.write(TradeHistoryPage().render())
