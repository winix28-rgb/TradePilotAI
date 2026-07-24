"""
===========================================================
TradePilotAI
Trade Order
===========================================================

Represents an order ready for execution.
"""

from dataclasses import dataclass, field
from datetime import datetime

from signals.signal_types import SignalType


@dataclass(slots=True)
class TradeOrder:
    """
    Represents an executable trade order.
    """

    symbol: str
    action: SignalType

    quantity: float
    price: float

    stop_loss: float | None = None
    take_profit: float |None = None

    strategy: str = ""

    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def value(self) -> float:
        """
        Total value of the order.
        """
        return self.quantity * self.price