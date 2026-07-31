"""Broker interfaces for the TradePilotAI OS."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from tradepilotai_os.models.trade import Trade
from tradepilotai_os.operations.logging_service import create_logger


@dataclass(slots=True)
class ExecutionResult:
    """Represents the result of an execution request."""

    success: bool
    message: str
    trade: Trade | None = None
    metadata: dict[str, Any] | None = None


class BrokerInterface(ABC):
    """Abstract interface for exchanging trade execution logic."""

    def __init__(self) -> None:
        self.logger = create_logger("TradePilotAI")

    @abstractmethod
    def execute(self, trade: Trade) -> ExecutionResult:
        """Execute a trade proposal through the broker implementation."""


class Broker(BrokerInterface):
    """Backward-compatible broker abstraction alias."""

    pass
