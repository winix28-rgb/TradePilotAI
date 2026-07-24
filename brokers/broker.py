"""
===========================================================
TradePilotAI
Broker Interface
===========================================================

Defines the behaviour of every broker implementation.
"""

from abc import ABC, abstractmethod

from models.position import Position
from models.trade_order import TradeOrder


class Broker(ABC):
    """
    Abstract broker interface.

    Every broker implementation (paper or live) is responsible
    for executing an approved TradeOrder and returning the
    resulting Position.
    """

    @abstractmethod
    def execute(self, order: TradeOrder) -> Position:
        """
        Execute a trade order and return the opened position.
        """
        raise NotImplementedError