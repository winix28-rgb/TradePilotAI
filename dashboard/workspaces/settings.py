"""Settings workspace renderer."""

from __future__ import annotations

from typing import Any

def render_settings_workspace(state: Any) -> None:
    """Render the settings workspace."""
    from dashboard.app import render_system_status

    render_system_status(state)
