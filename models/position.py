"""
===========================================================
TradePilotAI
Position Model
===========================================================

Represents an OPEN position in the portfolio.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Position:
    """
    Represents an open position.
    """

    symbol: str
    entry_date: datetime
    entry_price: float
    shares: int

    @property
    def cost(self) -> float:
        """
        Original amount invested.
        """
        return self.entry_price * self.shares