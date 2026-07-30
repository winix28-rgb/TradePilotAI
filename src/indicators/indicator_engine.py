"""
===========================================================
FTSE Quant Trader V2
Indicator Engine
===========================================================

Adds technical indicators to market data.
"""

import pandas as pd

from indicators.ema import EMA
from indicators.rsi import RSI


class IndicatorEngine:
    """
    Calculates technical indicators.
    """

    def __init__(self):
        print("Indicator Engine Initialised")

    def add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to market data.
        """

        data = data.copy()

        print("Calculating EMA 12...")
        data["EMA12"] = EMA.calculate(data, 12)

        print("Calculating EMA 26...")
        data["EMA26"] = EMA.calculate(data, 26)

        print("Calculating RSI 14...")
        data["RSI"] = RSI.calculate(data, 14)

        print("Indicators Added Successfully")

        return data