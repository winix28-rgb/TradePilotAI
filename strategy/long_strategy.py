"""
===========================================================
TradePilotAI
Long Strategy
Version 3.0
===========================================================

Handles all long trade logic.
"""

from models.strategy_state import StrategyState, StrategyStatus
from signals.signal_engine import SignalEngine
from config import settings


class LongStrategy:
    """
    Handles the long side of the trading strategy.
    """

    @staticmethod
    def process(previous, current, state: StrategyState):
        """
        Process one candle of market data.

        Parameters
        ----------
        previous : pandas.Series
            Previous candle.

        current : pandas.Series
            Current candle.

        state : StrategyState
            Current strategy state.

        Returns
        -------
        StrategyState
            Updated strategy state.
        """

        # --------------------------------------------------
        # IDLE
        # --------------------------------------------------

        if state.state == StrategyStatus.IDLE:

            if SignalEngine.is_rsi_oversold(
                current["RSI"],
                settings.BUY_RSI
            ):

                state.state = StrategyStatus.WATCHING_LONG
                state.lowest_low = current["Low"]
                state.setup_age = 0

            return state

        # --------------------------------------------------
        # WATCHING LONG
        # --------------------------------------------------

        if state.state == StrategyStatus.WATCHING_LONG:

            state.lowest_low = min(
                state.lowest_low,
                current["Low"]
            )

            if current["RSI"] > settings.BUY_RSI:

                state.state = StrategyStatus.READY_TO_BUY
                state.setup_age = 0

            return state

        # --------------------------------------------------
        # READY TO BUY
        # --------------------------------------------------

        if state.state == StrategyStatus.READY_TO_BUY:

            state.setup_age += 1

            if state.setup_age > settings.SETUP_TIMEOUT:

                state.state = StrategyStatus.IDLE
                state.lowest_low = None
                state.setup_age = 0

                return state

            if SignalEngine.bullish_crossover(previous, current):

                state.state = StrategyStatus.LONG
                state.entry_price = current["Close"]
                state.stop_loss = state.lowest_low
                state.entry_time = current.name

            return state

        # --------------------------------------------------
        # LONG
        # --------------------------------------------------

        if state.state == StrategyStatus.LONG:

            # Exit handled later by Strategy Engine
            return state

        return state