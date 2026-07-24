"""
===========================================================
TradePilotAI
Indicator Engine
Version 3.0
===========================================================

Calculates technical indicators used by all strategies.
"""

import pandas as pd


class IndicatorEngine:
    """
    Calculates technical indicators for market data.
    """

    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.
        """
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        """

        delta = series.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        average_gain = gain.ewm(
            alpha=1 / period,
            min_periods=period,
            adjust=False
        ).mean()

        average_loss = loss.ewm(
            alpha=1 / period,
            min_periods=period,
            adjust=False
        ).mean()

        rs = average_gain / average_loss

        return 100 - (100 / (1 + rs))

    @staticmethod
    def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """
        Add all standard indicators to the DataFrame.
        """

        df = data.copy()

        df["EMA12"] = IndicatorEngine.ema(df["Close"], 12)
        df["EMA26"] = IndicatorEngine.ema(df["Close"], 26)
        df["RSI"] = IndicatorEngine.rsi(df["Close"], 14)

        return df