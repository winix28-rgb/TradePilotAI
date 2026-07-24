"""
===========================================================
TradePilotAI
Trade Engine
===========================================================

Coordinates the execution of approved trade orders.
"""

from brokers.broker import Broker
from models.position import Position
from models.trade_order import TradeOrder
from portfolio.portfolio_manager import PortfolioManager


class TradeEngine:
    """
    Coordinates order execution.
    """

    def __init__(
        self,
        broker: Broker,
        portfolio: PortfolioManager,
    ):
        self._broker = broker
        self._portfolio = portfolio

    @property
    def broker(self) -> Broker:
        return self._broker

    @property
    def portfolio(self) -> PortfolioManager:
        return self._portfolio

    def execute(self, order: TradeOrder) -> Position:
        """
        Execute an approved BUY order.
        """

        if not isinstance(order, TradeOrder):
            raise TypeError(
                "execute() expects a TradeOrder."
            )

        position = self.broker.execute(order)

        self.portfolio.add_position(position)

        return position