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
    strategy_id = "rsi_mean_reversion"
    name = "TradePilotAI RSI Mean Reversion"
    asset_class = "Equities"
    primary_timeframe = "1h"
    supported_timeframes = ["1h", "2h"]
    description = "Mean reversion strategy using RSI extremes with EMA crossover confirmation."

    def evaluate(
        self,
        symbol: str,
        data,
    ):

        return SignalEngine.evaluate(
            symbol,
            data,
        )