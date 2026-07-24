"""
===========================================================
TradePilotAI
Trade Model
===========================================================

Represents a completed trade.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Trade:
    """
    Represents a completed trade.
    """

    symbol: str

    quantity: float

    entry_price: float
    exit_price: float

    entry_date: datetime
    exit_date: datetime

    strategy: str = ""

    @property
    def cost(self) -> float:
        """
        Original capital committed.
        """
        return self.entry_price * self.quantity

    @property
    def proceeds(self) -> float:
        """
        Cash received when the position was closed.
        """
        return self.exit_price * self.quantity

    @property
    def profit(self) -> float:
        """
        Realised profit or loss.
        """
        return self.proceeds - self.cost

    @property
    def return_percent(self) -> float:
        """
        Percentage return.
        """
        if self.cost == 0:
            return 0.0

        return (self.profit / self.cost) * 100

    @property
    def duration(self):
        """
        Time spent in the trade.
        """
        return self.exit_date - self.entry_date