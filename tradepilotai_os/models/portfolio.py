"""Portfolio model for paper trading workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .position import Position


@dataclass(slots=True)
class Portfolio:
    """Represents the current portfolio state."""

    cash: float = 0.0
    realised_pnl: float = 0.0
    unrealised_pnl: float = 0.0
    exposure: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
