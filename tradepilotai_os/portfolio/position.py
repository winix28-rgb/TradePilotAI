"""Position model for the TradePilotAI OS portfolio layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Position:
    """Represents a current open position for a symbol."""

    symbol: str
    quantity: int = 0
    average_price: float = 0.0
    market_price: float = 0.0
    exposure: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
