"""
===========================================================
TradePilotAI OS
Indicator Engine
===========================================================

Calculates all technical indicators used throughout
the platform.
"""

from __future__ import annotations

import pandas as pd


class IndicatorEngine:

    @staticmethod
    def add_indicators(data: pd.DataFrame) -> pd.DataFrame:

        data = data.copy()

        close = data["Close"]

        # -----------------------
        # EMA
        # -----------------------

        data["EMA12"] = close.ewm(
            span=12,
            adjust=False,
        ).mean()

        data["EMA26"] = close.ewm(
            span=26,
            adjust=False,
        ).mean()

        # -----------------------
        # RSI
        # -----------------------

        delta = close.diff()

        gain = delta.where(delta > 0, 0)

        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(14).mean()

        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        data["RSI"] = 100 - (100 / (1 + rs))

        # -----------------------
        # EMA Cross
        # -----------------------

        data["EMA_Bullish"] = (
            data["EMA12"] > data["EMA26"]
        )

        data["EMA_Bearish"] = (
            data["EMA12"] < data["EMA26"]
        )

        return data