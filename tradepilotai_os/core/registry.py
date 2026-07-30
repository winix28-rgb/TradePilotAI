"""
============================================================
TradePilotAI Operating System
Service Registry
============================================================
"""

from __future__ import annotations

from .container import Container


class ServiceRegistry:
    """
    Central registry for application services.
    """

    def __init__(self, container: Container) -> None:
        self._container = container

    @property
    def container(self) -> Container:
        return self._container

    def register_singleton(self, name: str, instance: object) -> None:
        self._container.register_singleton(name, instance)

    def register_factory(self, name: str, factory) -> None:
        self._container.register_factory(name, factory)

    def resolve(self, name: str):
        return self._container.resolve(name)

    def contains(self, name: str) -> bool:
        return self._container.contains(name)

    def remove(self, name: str) -> None:
        self._container.remove(name)

    def clear(self) -> None:
        self._container.clear()

    def services(self) -> list[str]:
        return self._container.registered_services()