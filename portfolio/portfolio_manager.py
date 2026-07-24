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
    Manages account and open positions.
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

        if position.symbol in self._positions:
            raise ValueError(f"{position.symbol} already exists.")

        self._positions[position.symbol] = position

    def remove_position(self, symbol: str) -> None:

        if symbol not in self._positions:
            raise ValueError(f"{symbol} not found.")

        del self._positions[symbol]

    def has_position(self, symbol: str) -> bool:

        return symbol in self._positions

    def get_position(self, symbol: str) -> Position | None:

        return self._positions.get(symbol)

    @property
    def portfolio_value(self) -> float:

        return sum(
            position.market_value
            for position in self._positions.values()
        )

    @property
    def total_value(self) -> float:

        return self.account.cash + self.portfolio_value