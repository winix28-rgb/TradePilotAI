"""Navigation service for TradePilotAI OS pages."""

from __future__ import annotations

from typing import Any


class NavigationService:
    """Provide route registration, page resolution, and breadcrumbs."""

    def __init__(self) -> None:
        self._routes: dict[str, Any] = {}
        self._current_route: str | None = None

    def register(self, route: str, target: Any) -> None:
        """Register a route name to a page target."""

        self._routes[route] = target

    def navigate(self, route: str) -> Any:
        """Resolve and remember a route."""

        self._current_route = route
        return self._routes.get(route)

    def current_route(self) -> str | None:
        """Return the current route name."""

        return self._current_route

    def breadcrumbs(self, route: str, parent: str | None = None) -> list[str]:
        """Build a breadcrumb trail for a route."""

        items = ["Dashboard"]
        if parent is not None:
            items.append(self._routes.get(parent, parent))
        items.append(self._routes.get(route, route))
        return items

    def resolve_dashboard_target(self, route: str) -> str:
        """Resolve a target route from a dashboard card selection."""

        return route
