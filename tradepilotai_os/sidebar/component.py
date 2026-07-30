"""Reusable sidebar component for the TradePilotAI OS shell."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService


class Sidebar:
    """Render a reusable sidebar with route-aware navigation items."""

    def __init__(self, navigation_service: NavigationService | None = None, active_route: str | None = None) -> None:
        self.navigation_service = navigation_service or NavigationService()
        self.active_route = active_route

    def render(self) -> str:
        """Render the sidebar sections and items."""

        items = [
            ("Dashboard", "dashboard"),
            ("Live Trading", "live_trading"),
            ("Scanner", "scanner"),
            ("Orders", "orders"),
            ("Backtesting", "backtesting"),
            ("Strategy Centre", "strategy_centre"),
            ("Risk", "risk"),
            ("Holdings", "portfolio"),
            ("Trade History", "trade_history"),
            ("Settings", "settings"),
        ]

        lines = ["Sidebar", "Dashboard", "Trading", "Analytics", "Portfolio", "Settings"]
        for label, route in items:
            marker = "[active]" if self.active_route == route else ""
            lines.append(f"{label}{marker}".strip())

        return "\n".join(lines)
