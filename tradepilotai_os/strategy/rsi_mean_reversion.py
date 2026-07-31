"""
===========================================================
TradePilotAI OS
RSI Mean Reversion Strategy
===========================================================
"""

from __future__ import annotations

from tradepilotai_os.signals.signal_engine import SignalEngine
from tradepilotai_os.strategy.base_strategy import BaseStrategy


class RSIMeanReversionStrategy(BaseStrategy):

    def evaluate(
        self,
        symbol: str,
        data,
    ):

        return SignalEngine.evaluate(
            symbol,
            data,
        )