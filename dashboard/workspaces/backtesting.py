"""Backtesting workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from tradepilotai_os.backtesting import BacktestingPage


def render_backtesting_workspace(state: Any) -> None:
    """Render the backtesting workspace."""
    st.write(BacktestingPage().render())
