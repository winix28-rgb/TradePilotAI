"""
===========================================================
TradePilotAI OS
Strategy Engine
===========================================================
"""

from __future__ import annotations

from tradepilotai_os.models.signal import Signal
from tradepilotai_os.models.strategy_state import StrategyState
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.strategy.rsi_mean_reversion import (
    RSIMeanReversionStrategy,
)


class StrategyEngine:

    def __init__(self):

        self.strategy = RSIMeanReversionStrategy()

    @property
    def primary_timeframe(self) -> str:
        return str(getattr(self.strategy, "primary_timeframe", ""))

    def evaluate(
        self,
        symbol,
        data,
    ):

        return self.strategy.evaluate(
            symbol,
            data,
        )

    def evaluate_signal(self, symbol: str, signal: Signal) -> tuple[StrategyState, list[Trade]]:
        """Translate an abstract signal into a strategy state and trade objects."""
        state = StrategyState()
        trades: list[Trade] = []

        if signal.signal_type == "BUY":
            state.state = StrategyState.LONG
            trades.append(
                Trade(
                    ticker=symbol,
                    direction="BUY",
                    entry_time=None,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    quantity=1,
                    take_profit=signal.entry_price + 10.0,
                )
            )
        elif signal.signal_type == "SELL":
            state.state = StrategyState.SHORT
            trades.append(
                Trade(
                    ticker=symbol,
                    direction="SELL",
                    entry_time=None,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    quantity=1,
                    take_profit=signal.entry_price - 10.0,
                )
            )
        else:
            state.state = StrategyState.IDLE

        return state, trades