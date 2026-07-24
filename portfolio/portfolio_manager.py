"""
===========================================================
TradePilotAI
Portfolio Manager
===========================================================

Manages the trading account and open positions.
"""

from models.position import Position
from portfolio.account import Account


class PortfolioManager:
    """
    Manages the trading account and open positions.
    """

    def __init__(self, account: Account):

        self._account = account
        self._positions: dict[str, Position] = {}

    @property
    def account(self) -> Account:
        return self._account

    @property
    def positions(self) -> dict[str, Position]:
        return self._positions

    def add_position(self, position: Position) -> None:
        """
        Add a new position to the portfolio.
        """

        if self.has_position(position.symbol):
            raise ValueError(f"{position.symbol} already exists.")

        self._positions[position.symbol] = position

    def remove_position(self, symbol: str) -> Position:
        """
        Remove and return a position.
        """

        if not self.has_position(symbol):
            raise ValueError(f"{symbol} not found.")

        return self._positions.pop(symbol)

    def has_position(self, symbol: str) -> bool:
        """
        Returns True if the portfolio owns the symbol.
        """
        return symbol in self._positions

    def get_position(self, symbol: str) -> Position | None:
        """
        Return a position or None if it doesn't exist.
        """
        return self._positions.get(symbol)

    @property
    def portfolio_value(self) -> float:
        """
        Current market value of all open positions.
        """
        return sum(
            position.market_value
            for position in self._positions.values()
        )

    @property
    def total_value(self) -> float:
        """
        Total account value.
        """
        return self.account.cash + self.portfolio_value