"""Position model for paper trading workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Position:
    """Represents an open trading position."""

    symbol: str
    quantity: int = 0
    average_price: float = 0.0
    market_price: float = 0.0
    exposure: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
