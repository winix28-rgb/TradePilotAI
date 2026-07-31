"""Centralized structured logging for TradePilotAI OS."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Iterator


class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(slots=True)
class LogEntry:
    timestamp: str
    level: str
    module: str
    message: str
    correlation_id: str | None = None
    exception: str | None = None
    context: dict[str, Any] | None = None


class StructuredLogger:
    """Structured logger with correlation IDs and module-aware formatting."""

    def __init__(self, name: str = "TradePilotAI", correlation_id: str | None = None) -> None:
        self.name = name
        self.correlation_id = correlation_id
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)
        handlers = list(_configured_handlers)
        if not handlers:
            configure_logging()
            handlers = list(_configured_handlers)

        self._logger.propagate = False
        for handler in list(self._logger.handlers):
            self._logger.removeHandler(handler)
            handler.close()
        for handler in handlers:
            self._logger.addHandler(handler)

    def debug(self, message: str, module: str = "application", **context: Any) -> None:
        self._emit(LogLevel.DEBUG, message, module, **context)

    def info(self, message: str, module: str = "application", **context: Any) -> None:
        self._emit(LogLevel.INFO, message, module, **context)

    def warning(self, message: str, module: str = "application", **context: Any) -> None:
        self._emit(LogLevel.WARNING, message, module, **context)

    def error(self, message: str, module: str = "application", **context: Any) -> None:
        self._emit(LogLevel.ERROR, message, module, **context)

    def critical(self, message: str, module: str = "application", **context: Any) -> None:
        self._emit(LogLevel.CRITICAL, message, module, **context)

    def exception(self, message: str, module: str = "application", exc: Exception | None = None, **context: Any) -> None:
        payload = {"exception": repr(exc) if exc is not None else None}
        payload.update(context)
        self._emit(LogLevel.ERROR, message, module, **payload)

    def _emit(self, level: str, message: str, module: str, **context: Any) -> None:
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            module=module,
            message=message,
            correlation_id=self.correlation_id or get_current_correlation_id(),
            context=context or None,
        )
        payload = {
            "timestamp": entry.timestamp,
            "level": entry.level,
            "module": entry.module,
            "message": entry.message,
            "correlation_id": entry.correlation_id,
            "thread": "main",
            "context": entry.context,
        }
        record = json.dumps(payload)
        self._logger.log(self._log_level(level), record)
        for handler in self._logger.handlers:
            handler.flush()

    def _log_level(self, level: str) -> int:
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(level, logging.INFO)


_current_correlation_id: str | None = None
_configured_handlers: list[logging.Handler] = []


def configure_logging(
    level: str = "INFO",
    log_file: str | None = None,
    console_enabled: bool = True,
    file_enabled: bool = True,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> None:
    """Configure the root logger with console/file handlers and rotation support."""

    logging_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter("%(message)s")
    handlers: list[logging.Handler] = []

    if console_enabled:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

    if file_enabled:
        target = log_file or os.getenv("TRADEPILOT_LOG_FILE", "logs/tradepilotai.log")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        file_handler = RotatingFileHandler(
            target,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    global _configured_handlers
    _configured_handlers = handlers

    for handler in handlers:
        root_logger.addHandler(handler)


@contextmanager
def correlation_context(correlation_id: str) -> Iterator[None]:
    """Temporarily bind a correlation ID for downstream logging."""

    global _current_correlation_id
    previous = _current_correlation_id
    _current_correlation_id = correlation_id
    try:
        yield
    finally:
        _current_correlation_id = previous


def get_current_correlation_id() -> str | None:
    return _current_correlation_id


def create_logger(name: str = "TradePilotAI", correlation_id: str | None = None) -> StructuredLogger:
    return StructuredLogger(name=name, correlation_id=correlation_id)
