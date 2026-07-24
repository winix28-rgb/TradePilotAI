"""
===========================================================
TradePilotAI
RSI Mean Reversion Strategy
===========================================================

First production strategy.

Entry Rules
-----------
1. RSI falls below BUY_RSI.
2. Record the lowest price while RSI remains oversold.
3. Wait for EMA12 to cross above EMA26.
4. Generate BUY signal.

Exit Rules
----------
1. RSI reaches EXIT_RSI.
"""

from models.strategy_state import StrategyState, StrategyStatus
from strategies.base_strategy import BaseStrategy
from signals.signal_types import SignalType


class RSIMeanReversionStrategy(BaseStrategy):

    def __init__(self):
        super().__init__()

    def reset(self):

        self.state = StrategyState()

    def on_bar(self, previous, current):

        signal = SignalType.NONE

        # ---------------------------------------------------
        # Looking for oversold market
        # ---------------------------------------------------

        if self.state.state == StrategyStatus.IDLE:

            if current["RSI"] <= 30:

                self.state.state = StrategyStatus.WATCHING_LONG
                self.state.lowest_low = current["Low"]

        # ---------------------------------------------------
        # Continue watching
        # ---------------------------------------------------

        elif self.state.state == StrategyStatus.WATCHING_LONG:

            if current["Low"] < self.state.lowest_low:
                self.state.lowest_low = current["Low"]

            bullish_cross = (
                previous["EMA12"] <= previous["EMA26"]
                and current["EMA12"] > current["EMA26"]
            )

            if bullish_cross:

                self.state.state = StrategyStatus.LONG

                self.state.entry_price = current["Close"]

                self.state.stop_loss = self.state.lowest_low

                signal = SignalType.BUY

        # ---------------------------------------------------
        # Already long
        # ---------------------------------------------------

        elif self.state.state == StrategyStatus.LONG:

            if current["RSI"] >= 50:

                self.state.state = StrategyStatus.IDLE

                signal = SignalType.SELL

        return signal