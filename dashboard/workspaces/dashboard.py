"""Dashboard workspace renderer."""

from __future__ import annotations

from typing import Any

def render_dashboard_workspace(state: Any) -> None:
    """Render the dashboard workspace through the existing dashboard layout."""
    from dashboard.app import render_dashboard as _render_dashboard

    _render_dashboard(state)
