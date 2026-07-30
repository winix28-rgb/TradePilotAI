"""Order model for paper trading workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class Order:
    """Represents a trading order in a simulation or paper-trading context."""

    order_id: str
    symbol: str
    side: str
    quantity: int
    price: Optional[float] = None
    order_type: str = "MARKET"
    status: str = "NEW"
    metadata: dict[str, Any] = field(default_factory=dict)
