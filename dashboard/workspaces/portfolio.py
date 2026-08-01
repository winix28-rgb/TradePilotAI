"""Portfolio workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from tradepilotai_os.portfolio import PortfolioPage


def render_portfolio_workspace(state: Any) -> None:
    """Render the portfolio workspace."""
    st.write(PortfolioPage().render())
