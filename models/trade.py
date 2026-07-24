"""
===========================================================
TradePilotAI
Trade Model
===========================================================

Represents one completed trade.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Trade:
    """
    Represents a completed trade.
    """

    symbol: str

    entry_date: datetime
    exit_date: datetime

    entry_price: float
    exit_price: float

    quantity: float = 1.0

    exit_reason: str = ""

    @property
    def profit(self) -> float:
        return (self.exit_price - self.entry_price) * self.quantity

    @property
    def return_percent(self) -> float:
        return (
            (self.exit_price - self.entry_price)
            / self.entry_price
        ) * 100

    @property
    def duration_days(self) -> int:
        return (self.exit_date - self.entry_date).days