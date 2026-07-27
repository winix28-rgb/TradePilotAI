"""
===========================================================
TradePilotAI
Indicator Engine
===========================================================

Combines price data with calculated indicators.
"""

from __future__ import annotations

from backtesting.candle import Candle

from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi


class IndicatorEngine:
    """
    Calculates indicators and creates strategy-ready bars.
    """

    def __init__(
        self,
        ema_fast: int = 12,
        ema_slow: int = 26,
        rsi_period: int = 14,
    ):

        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period


    def calculate(
        self,
        candles: list[Candle],
    ) -> list[dict]:
        """
        Convert candles into indicator enriched bars.
        """

        if not candles:
            return []


        closes = [
            candle.close
            for candle in candles
        ]


        ema_fast_values = calculate_ema(
            closes,
            self.ema_fast,
        )


        ema_slow_values = calculate_ema(
            closes,
            self.ema_slow,
        )


        rsi_values = calculate_rsi(
            closes,
            self.rsi_period,
        )


        bars = []


        for index, candle in enumerate(candles):

            bars.append(
                {
                    "Open": candle.open,
                    "High": candle.high,
                    "Low": candle.low,
                    "Close": candle.close,
                    "Volume": candle.volume,

                    f"EMA{self.ema_fast}":
                        ema_fast_values[index],

                    f"EMA{self.ema_slow}":
                        ema_slow_values[index],

                    "RSI":
                        rsi_values[index],
                }
            )


        return bars