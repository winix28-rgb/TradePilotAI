"""Strategy state model for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class StrategyState:
    """Represents the current workflow state of a strategy instance."""

    IDLE: str = "IDLE"
    WATCHING_LONG: str = "WATCHING_LONG"
    READY_TO_BUY: str = "READY_TO_BUY"
    LONG: str = "LONG"
    WATCHING_SHORT: str = "WATCHING_SHORT"
    READY_TO_SELL: str = "READY_TO_SELL"
    SHORT: str = "SHORT"

    state: str = IDLE
    lowest_low: Optional[float] = None
    setup_age: int = 0
    highest_high: Optional[float] = None
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    entry_index: Optional[int] = None
    entry_time: Optional[Any] = None
    metadata: dict[str, Any] = field(default_factory=dict)
