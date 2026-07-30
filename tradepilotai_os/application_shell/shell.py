"""Reusable application shell for TradePilotAI OS pages."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService


class ApplicationShell:
    """Render a reusable root layout for the application."""

    def __init__(self, navigation_service: NavigationService | None = None) -> None:
        self.navigation_service = navigation_service or NavigationService()
        self._current_page: Any | None = None

    def show(self, route: str) -> None:
        """Select the current page for the shell to render."""

        self._current_page = self.navigation_service.navigate(route)

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
