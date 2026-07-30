"""Broker interfaces for the TradePilotAI OS."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from tradepilotai_os.models.trade import Trade


@dataclass(slots=True)
class ExecutionResult:
    """Represents the result of an execution request."""

    success: bool
    message: str
    trade: Trade | None = None
    metadata: dict[str, Any] | None = None


class Broker(ABC):
    """Abstract interface for exchanging trade execution logic."""

    @abstractmethod
    def execute(self, trade: Trade) -> ExecutionResult:
        """Execute a trade proposal through the broker implementation."""
