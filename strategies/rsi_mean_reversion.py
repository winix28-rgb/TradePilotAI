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
3. Wait for EMA Fast to cross above EMA Slow.
4. Generate BUY signal.

Exit Rules
----------
1. RSI reaches EXIT_RSI.
"""

from models.strategy_config import StrategyConfig
from models.strategy_state import StrategyState, StrategyStatus
from signals.signal_types import SignalType
from strategies.base_strategy import BaseStrategy


class RSIMeanReversionStrategy(BaseStrategy):

    def __init__(
        self,
        config: StrategyConfig | None = None,
    ):
        super().__init__(config)

    def reset(self):

        self.state = StrategyState()

    def on_bar(self, previous, current):

        signal = SignalType.NONE

        fast = f"EMA{self.config.ema_fast}"
        slow = f"EMA{self.config.ema_slow}"

        # ---------------------------------------------------
        # Looking for oversold market
        # ---------------------------------------------------

        if self.state.state == StrategyStatus.IDLE:

            if current["RSI"] <= self.config.buy_rsi:

                self.state.state = StrategyStatus.WATCHING_LONG
                self.state.lowest_low = current["Low"]

        # ---------------------------------------------------
        # Continue watching
        # ---------------------------------------------------

        elif self.state.state == StrategyStatus.WATCHING_LONG:

            if current["Low"] < self.state.lowest_low:
                self.state.lowest_low = current["Low"]

            bullish_cross = (
                previous[fast] <= previous[slow]
                and current[fast] > current[slow]
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

            if current["RSI"] >= self.config.exit_rsi:

                self.state.state = StrategyStatus.IDLE
                signal = SignalType.SELL

        return signal