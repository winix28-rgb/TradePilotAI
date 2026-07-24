"""
===========================================================
TradePilotAI
Base Strategy
Version 3.0
===========================================================

Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    """

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def on_bar(
        self,
        previous: pd.Series,
        current: pd.Series,
    ):
        """
        Process one candle of market data.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset strategy state.
        """
        pass