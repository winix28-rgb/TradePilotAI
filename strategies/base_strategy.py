"""
===========================================================
TradePilotAI
Base Strategy
===========================================================

Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod

import pandas as pd

from models.strategy_config import StrategyConfig
from models.strategy_state import StrategyState


class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    """

    def __init__(
        self,
        config: StrategyConfig | None = None,
    ):
        self.config = config or StrategyConfig()
        self.state = StrategyState()
        self.name = self.__class__.__name__

    @abstractmethod
    def on_bar(
        self,
        previous: pd.Series,
        current: pd.Series,
    ):
        """
        Process one market bar.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self):
        """
        Reset the strategy to its initial state.
        """
        raise NotImplementedError