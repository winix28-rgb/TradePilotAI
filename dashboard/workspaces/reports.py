"""Reports workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.views.performance_view import render_performance


def render_reports_workspace(state: Any) -> None:
    """Render the reports workspace."""
    render_performance(state)
