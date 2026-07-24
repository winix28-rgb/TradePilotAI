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
from models.trade_order import TradeOrder


class Broker(ABC):
    """
    Abstract broker interface.
    """

    @abstractmethod
    def execute(
        self,
        order: TradeOrder,
    ) -> Position:
        """
        Execute a trade order.
        """
        raise NotImplementedError