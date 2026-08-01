"""Risk workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from tradepilotai_os.risk import RiskDashboardPage


def render_risk_workspace(state: Any) -> None:
    """Render the risk workspace."""
    st.write(RiskDashboardPage().render())
