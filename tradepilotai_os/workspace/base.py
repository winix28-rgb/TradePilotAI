"""Base class for TradePilotAI OS workspace pages."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import Breadcrumb, SectionHeader, StatusBar, Toolbar


class WorkspacePage:
    """Shared base class for workspace pages with common rendering states."""

    def __init__(self, page_title: str = "Workspace", navigation_service: NavigationService | None = None) -> None:
        self.page_title = page_title
        self.navigation_service = navigation_service or NavigationService()
        self.loading = False
        self.error: str | None = None
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        raise NotImplementedError

    def build_breadcrumbs(self, route_key: str, label: str) -> str:
        current_route = self.navigation_service.current_route() or route_key
        items = ["Dashboard", label]
        if current_route and current_route != route_key:
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def build_title(self, title: str, subtitle: str | None = None) -> str:
        return SectionHeader(title=title, subtitle=subtitle).render()

    def build_toolbar(self, title: str, actions: list[str] | None = None) -> str:
        return Toolbar(title=title, actions=actions or []).render()

    def build_status_bar(self, container: Any | None = None) -> str:
        return StatusBar(container=container, version="1.0.0").render()

    def build_loading_state(self) -> str:
        return "Loading..."

    def build_empty_state(self, message: str = "No data available") -> str:
        return message

    def build_error_state(self, message: str) -> str:
        return f"Error: {message}"

    def refresh(self) -> None:
        self.loading = True
        self.loading = False
