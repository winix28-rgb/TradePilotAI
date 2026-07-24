"""
===========================================================
TradePilotAI
Position Model
===========================================================

Represents an open trading position.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Position:
    """
    Represents an open trading position.
    """

    symbol: str
    quantity: float
    entry_price: float

    current_price: float

    entry_date: datetime = field(default_factory=datetime.now)

    stop_loss: float | None = None
    take_profit: float | None = None

    strategy: str = ""

    notes: str = ""

    @property
    def cost(self) -> float:
        """Total amount originally invested."""
        return self.quantity * self.entry_price

    @property
    def market_value(self) -> float:
        """Current market value."""
        return self.quantity * self.current_price

    @property
    def unrealised_profit(self) -> float:
        """Current unrealised profit/loss."""
        return self.market_value - self.cost

    @property
    def unrealised_return(self) -> float:
        """Current percentage return."""
        if self.cost == 0:
            return 0.0

        return (self.unrealised_profit / self.cost) * 100

    def update_price(self, price: float) -> None:
        """
        Updates the latest market price.
        """

        if price <= 0:
            raise ValueError("Price must be greater than zero.")

        self.current_price = price