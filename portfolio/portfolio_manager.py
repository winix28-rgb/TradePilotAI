"""
===========================================================
TradePilotAI
Portfolio Manager
===========================================================

Maintains portfolio cash and open positions.
"""

from datetime import datetime

from models.position import Position


class PortfolioManager:
    """
    Maintains portfolio state.
    """

    def __init__(self, starting_cash: float):

        self.starting_cash = starting_cash
        self.cash = starting_cash

        self.positions: dict[str, Position] = {}

    @property
    def invested(self) -> float:
        """
        Total amount currently invested.
        """
        return sum(position.cost for position in self.positions.values())

    @property
    def total_value(self) -> float:
        """
        Cash + invested capital.
        """
        return self.cash + self.invested

    def can_afford(
        self,
        shares: int,
        price: float,
    ) -> bool:

        return (shares * price) <= self.cash

    def buy(
        self,
        symbol: str,
        shares: int,
        price: float,
    ) -> bool:
        """
        Purchase shares.
        """

        cost = shares * price

        if cost > self.cash:
            return False

        self.cash -= cost

        self.positions[symbol] = Position(
            symbol=symbol,
            entry_date=datetime.now(),
            entry_price=price,
            shares=shares,
        )

        return True

    def sell(
        self,
        symbol: str,
        price: float,
    ) -> bool:
        """
        Sell an entire position.
        """

        if symbol not in self.positions:
            return False

        position = self.positions.pop(symbol)

        self.cash += position.shares * price

        return True