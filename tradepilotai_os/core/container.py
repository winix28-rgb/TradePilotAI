"""
============================================================
TradePilotAI Operating System
Dependency Injection Container
============================================================
"""

from __future__ import annotations

from typing import Any, Callable


class Container:
    """
    Simple dependency injection container.

    Example:
        container.register_singleton("config", Config())
        container.register_factory("broker", Broker)

        config = container.resolve("config")
        broker = container.resolve("broker")
    """

    def __init__(self) -> None:

        self._singletons: dict[str, Any] = {}
        self._factories: dict[str, Callable[..., Any]] = {}

    # -----------------------------------------------------
    # Registration
    # -----------------------------------------------------

    def register_singleton(self, name: str, instance: Any) -> None:

        self._singletons[name] = instance

    def register_factory(
        self,
        name: str,
        factory: Callable[..., Any],
    ) -> None:

        self._factories[name] = factory

    # -----------------------------------------------------
    # Resolution
    # -----------------------------------------------------

    def resolve(self, name: str) -> Any:

        if name in self._singletons:
            return self._singletons[name]

        if name in self._factories:
            return self._factories[name]()

        raise KeyError(f"Service '{name}' is not registered.")

    # -----------------------------------------------------
    # Information
    # -----------------------------------------------------

    def contains(self, name: str) -> bool:

        return (
            name in self._singletons
            or name in self._factories
        )

    def remove(self, name: str) -> None:

        self._singletons.pop(name, None)
        self._factories.pop(name, None)

    def clear(self) -> None:

        self._singletons.clear()
        self._factories.clear()

    def singleton_count(self) -> int:

        return len(self._singletons)

    def factory_count(self) -> int:

        return len(self._factories)

    def service_count(self) -> int:

        return (
            self.singleton_count()
            + self.factory_count()
        )

    def registered_services(self) -> list[str]:

        names = list(self._singletons.keys())
        names.extend(self._factories.keys())

        return sorted(names)