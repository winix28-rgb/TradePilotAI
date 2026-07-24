"""
===========================================================
TradePilotAI
Broker Interface
===========================================================

Defines the interface all broker implementations must
follow.
"""

from abc import ABC, abstractmethod

from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder


class Broker(ABC):
    """
    Abstract broker interface.
    """

    @abstractmethod
    def execute(
        self,
        order: TradeOrder,
        position: Position | None = None,
    ) -> Position | Trade:
        """
        Execute a trade order.

        BUY orders do not require an existing position.

        SELL orders require the open Position being closed.
        """
        raise NotImplementedError