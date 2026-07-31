"""Reusable application shell for TradePilotAI OS pages."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import StatusBar
from tradepilotai_os.live_trading import LiveTradingPage
from tradepilotai_os.risk import RiskDashboardPage
from tradepilotai_os.strategy import StrategyPage
from tradepilotai_os.trade_history import TradeHistoryPage


class ApplicationShell:
    """Render a reusable root layout for the application."""

    def __init__(self, navigation_service: NavigationService | None = None) -> None:
        self.navigation_service = navigation_service or NavigationService()
        self._current_page: Any | None = None

    def show(self, route: str) -> None:
        """Select the current page for the shell to render."""

        self._current_page = self.navigation_service.navigate(route)
        if self._current_page is None and route == "trade_history":
            self._current_page = TradeHistoryPage()
        if self._current_page is None and route == "risk":
            self._current_page = RiskDashboardPage()
        if self._current_page is None and route == "live_trading":
            self._current_page = LiveTradingPage()
        if self._current_page is None and route == "strategy":
            self._current_page = StrategyPage()

    def render(self) -> str:
        """Render the shell layout including the active page content."""

        content = ""
        if self._current_page is not None and hasattr(self._current_page, "render"):
            content = self._current_page.render()
        elif self._current_page is not None:
            content = str(self._current_page)

        return "\n".join(
            [
                "Header",
                "Sidebar",
                "Main Content",
                content,
                "Status Bar",
            ]
        )
