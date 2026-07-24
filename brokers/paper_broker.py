"""
===========================================================
TradePilotAI
Paper Broker
===========================================================

Simulates order execution.
"""

from brokers.broker import Broker
from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder
from portfolio.simulation_account import SimulationAccount
from signals.signal_types import SignalType


class PaperBroker(Broker):
    """
    Paper trading broker.

    Executes approved TradeOrder objects.
    """

    def __init__(self, account: SimulationAccount):
        self.account = account

    def execute(
        self,
        order: TradeOrder,
        position: Position | None = None,
    ) -> Position | Trade:
        """
        Execute a trade order.
        """

        if order.action == SignalType.BUY:
            return self._execute_buy(order)

        if order.action == SignalType.SELL:

            if position is None:
                raise ValueError(
                    "SELL orders require an existing Position."
                )

            return self._execute_sell(order, position)

        raise ValueError(
            f"Unsupported order action: {order.action}"
        )

    def _execute_buy(
        self,
        order: TradeOrder,
    ) -> Position:
        """
        Execute a BUY order.
        """

        self.account.withdraw(order.value)

        return Position(
            symbol=order.symbol,
            quantity=order.quantity,
            entry_price=order.price,
            current_price=order.price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            strategy=order.strategy,
        )

    def _execute_sell(
        self,
        order: TradeOrder,
        position: Position,
    ) -> Trade:
        """
        Execute a SELL order.
        """

        trade = Trade(
            symbol=position.symbol,
            quantity=position.quantity,
            entry_price=position.entry_price,
            exit_price=order.price,
            entry_date=position.entry_date,
            exit_date=order.timestamp,
            strategy=position.strategy,
        )

        self.account.deposit(trade.proceeds)

        return trade