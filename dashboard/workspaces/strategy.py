"""Strategy workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from tradepilotai_os.strategy import StrategyPage


def render_strategy_workspace(state: Any) -> None:
    """Render the strategy workspace."""
    st.write(StrategyPage().render())
