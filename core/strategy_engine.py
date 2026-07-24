"""
===========================================================
TradePilotAI
Strategy Engine
===========================================================

Purpose
-------
Runs a trading strategy over historical market data and
passes all signals to the Trade Recorder.

Responsibilities
----------------
- Execute strategy.
- Feed signals to Trade Recorder.
- Return completed trades.
"""

import pandas as pd

from backtesting.trade_recorder import TradeRecorder
from strategies.base_strategy import BaseStrategy


class StrategyEngine:

    def __init__(self, strategy: BaseStrategy):

        self.strategy = strategy
        self.recorder = TradeRecorder()

    def run(self, data: pd.DataFrame):

        for i in range(1, len(data)):

            previous = data.iloc[i - 1]
            current = data.iloc[i]

            signal = self.strategy.on_bar(previous, current)

            self.recorder.process_signal(
                signal=signal,
                date=current.name,
                price=current["Close"],
            )

        return self.recorder.trades