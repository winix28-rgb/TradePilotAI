"""Execution report model for paper trading workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .order import Order


@dataclass(slots=True)
class ExecutionReport:
    """Represents a broker or simulator execution result."""

    order: Order
    success: bool
    message: str = ""
    filled_price: Optional[float] = None
    filled_quantity: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)
