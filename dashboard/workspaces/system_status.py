"""System Status workspace renderer."""

from __future__ import annotations

from typing import Any


def render_system_status_workspace(state: Any) -> None:
    """Render the release-readiness system status workspace."""
    from dashboard.app import render_system_status

    render_system_status(state)
