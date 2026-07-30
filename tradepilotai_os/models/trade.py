"""Trade model for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(slots=True)
class Trade:
    """Represents a trade lifecycle event from entry to exit."""

    ticker: str
    direction: str
    entry_time: Any
    entry_price: float
    stop_loss: float
    quantity: int = 1
    take_profit: Optional[float] = None
    exit_time: Optional[Any] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    profit: Optional[float] = None
    status: str = "OPEN"
