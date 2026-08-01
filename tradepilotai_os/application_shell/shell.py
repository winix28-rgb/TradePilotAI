"""Reusable application shell for TradePilotAI OS pages."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.backtesting import BacktestingPage
from tradepilotai_os.dashboard.page import DashboardPage
from tradepilotai_os.live_trading import LiveTradingPage
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.portfolio import PortfolioPage
from tradepilotai_os.risk import RiskDashboardPage
from tradepilotai_os.scanner import ScannerPage
from tradepilotai_os.strategy import StrategyPage
from tradepilotai_os.trade_history import TradeHistoryPage
from tradepilotai_os.ui_library import StatusBar


class _PlaceholderPage:
    """Fallback page used when a route does not yet have a dedicated workspace."""

    def __init__(self, title: str) -> None:
        self.title = title

    def render(self) -> str:
        return f"{self.title} workspace is under construction."


class ApplicationShell:
    """Render a reusable root layout for the application."""

    def __init__(self, navigation_service: NavigationService | None = None) -> None:
        self.navigation_service = navigation_service or NavigationService()
        self._current_page: Any | None = None

    def show(self, route: str) -> None:
        """Select the current page for the shell to render."""

        page = self.navigation_service.navigate(route)
        if page is None:
            page = self._resolve_default_page(route)
            if page is not None:
                self.navigation_service.register(route, page)

        self._current_page = page

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

    def _resolve_default_page(self, route: str) -> Any | None:
        mapping = {
            "dashboard": DashboardPage(),
            "home": DashboardPage(),
            "scanner": ScannerPage(),
            "portfolio": PortfolioPage(),
            "holdings": PortfolioPage(),
            "positions": LiveTradingPage(),
            "orders": LiveTradingPage(),
            "backtesting": BacktestingPage(),
            "trade_history": TradeHistoryPage(),
            "trades": TradeHistoryPage(),
            "risk": RiskDashboardPage(),
            "risk_management": RiskDashboardPage(),
            "risk-management": RiskDashboardPage(),
            "live_trading": LiveTradingPage(),
            "live-trading": LiveTradingPage(),
            "strategy": StrategyPage(),
            "strategy_centre": StrategyPage(),
            "strategies": StrategyPage(),
        }

        page = mapping.get(route)
        if page is None:
            return _PlaceholderPage(route.replace("_", " ").title())
        return page
