"""
===========================================================
TradePilotAI
Trade Engine
===========================================================

Coordinates the execution of approved trade orders.
"""

from brokers.broker import Broker
from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder
from portfolio.portfolio_manager import PortfolioManager
from signals.signal_types import SignalType


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

    def execute(
        self,
        order: TradeOrder,
    ) -> Position | Trade:
        """
        Execute an approved trade order.
        """

        if not isinstance(order, TradeOrder):
            raise TypeError(
                "execute() expects a TradeOrder."
            )

        if order.action == SignalType.BUY:

            position = self.broker.execute(order)

            self.portfolio.add_position(position)

            return position

        if order.action == SignalType.SELL:

            position = self.portfolio.get_position(order.symbol)

            if position is None:
                raise ValueError(
                    f"No open position exists for {order.symbol}."
                )

            trade = self.broker.execute(order, position)

            self.portfolio.remove_position(order.symbol)

            self.portfolio.record_trade(trade)

            return trade

        raise ValueError(
            f"Unsupported order action: {order.action}"
        )