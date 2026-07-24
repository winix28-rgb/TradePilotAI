"""
===========================================================
TradePilotAI
Paper Broker
===========================================================

Simulates order execution.
"""

from brokers.broker import Broker
from models.position import Position
from models.trade_order import TradeOrder
from portfolio.simulation_account import SimulationAccount


class PaperBroker(Broker):
    """
    Paper trading broker.

    Executes approved TradeOrder objects and returns the
    resulting Position.
    """

    def __init__(self, account: SimulationAccount):
        self.account = account

    def execute(self, order: TradeOrder) -> Position:
        """
        Execute a trade order.
        """

        cost = order.value

        self.account.withdraw(cost)

        return Position(
            symbol=order.symbol,
            quantity=order.quantity,
            entry_price=order.price,
            current_price=order.price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            strategy=order.strategy,
        )