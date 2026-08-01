"""Scanner workspace renderer."""

from __future__ import annotations

from typing import Any

from dashboard.views.scanner_view import render_scanner


def render_scanner_workspace(state: Any) -> None:
    """Render the scanner workspace through the polished dashboard view."""
    render_scanner(state)
