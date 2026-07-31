"""Event models and bus for the Risk Dashboard workspace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class RiskEvent:
    """Base event emitted when risk state changes."""

    name: str
    payload: dict[str, Any] | None = None


class EventBus:
    """Simple in-memory bus for risk-state notifications."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}

    def subscribe(self, event_name: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers.setdefault(event_name, []).append(handler)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        for handler in self._subscribers.get(event_name, []):
            handler(payload or {})
