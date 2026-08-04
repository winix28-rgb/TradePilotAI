"""Portfolio workspace renderer."""

from __future__ import annotations

from typing import Any

from dashboard.views.portfolio_view import render_portfolio


def render_portfolio_workspace(state: Any) -> None:
    """Render the portfolio workspace."""
    render_portfolio(state)
