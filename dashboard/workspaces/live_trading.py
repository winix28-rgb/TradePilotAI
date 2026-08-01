"""Live trading workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from tradepilotai_os.live_trading import LiveTradingPage


def render_live_trading_workspace(state: Any) -> None:
    """Render the live trading workspace."""
    st.write(LiveTradingPage().render())
