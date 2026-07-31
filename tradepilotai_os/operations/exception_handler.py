"""Centralized exception handling for TradePilotAI OS."""

from __future__ import annotations

from typing import Any, Callable

from .logging_service import StructuredLogger


class ExceptionHandler:
    """Capture unhandled exceptions and present friendly messages."""

    def __init__(self, logger: StructuredLogger | None = None) -> None:
        self.logger = logger or StructuredLogger("TradePilotAI")

    def handle(self, exc: Exception, context: str = "application") -> str:
        self.logger.error(str(exc), module=context, exception_type=type(exc).__name__)
        return f"Operational warning: {exc}"

    def wrap(self, func: Callable[..., Any], context: str = "application") -> Callable[..., Any]:
        def inner(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - defensive
                return self.handle(exc, context)

        return inner
