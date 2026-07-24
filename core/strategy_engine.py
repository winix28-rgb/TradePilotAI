"""
===========================================================
TradePilotAI
Strategy Engine
===========================================================

Runs any strategy that inherits from BaseStrategy.
"""

from typing import List
import pandas as pd

from signals.signal_types import SignalType
from strategies.base_strategy import BaseStrategy


class StrategyEngine:
    """
    Executes a strategy over historical market data.
    """

    def __init__(self, strategy: BaseStrategy):
        self.strategy = strategy

    def run(self, data: pd.DataFrame) -> List[SignalType]:
        """
        Run the strategy over the supplied market data.

        Returns
        -------
        List[SignalType]
            One signal per market bar.
        """

        signals = []

        for i in range(1, len(data)):

            previous = data.iloc[i - 1]
            current = data.iloc[i]

            signal = self.strategy.on_bar(previous, current)

            signals.append(signal)

        return signals