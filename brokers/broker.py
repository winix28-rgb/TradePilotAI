"""
===========================================================
TradePilotAI
Broker Interface
===========================================================

Defines the behaviour of every broker implementation.
"""

from abc import ABC, abstractmethod

from models.position import Position
from signals.trade_signal import TradeSignal


class Broker(ABC):
    """
    Abstract broker interface.
    """

    @abstractmethod
    def buy(self, signal: TradeSignal, quantity: float) -> Position:
        """
        Execute a buy order and return the opened position.
        """
        pass

    @abstractmethod
    def sell(self, symbol: str) -> Position:
        """
        Close a position and return it.
        """
        pass