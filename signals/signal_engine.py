"""
===========================================================
TradePilotAI
Signal Engine
Version 3.0
===========================================================

Evaluates trading signals from technical indicators.
"""

import pandas as pd


class SignalEngine:
    """
    Provides reusable trading signal methods.
    """

    @staticmethod
    def is_rsi_oversold(rsi: float, level: float = 30) -> bool:
        """
        Returns True when RSI is below the oversold level.
        """
        return rsi < level

    @staticmethod
    def is_rsi_overbought(rsi: float, level: float = 70) -> bool:
        """
        Returns True when RSI is above the overbought level.
        """
        return rsi > level

    @staticmethod
    def bullish_crossover(previous: pd.Series, current: pd.Series) -> bool:
        """
        Returns True when EMA12 crosses above EMA26.
        """

        return (
            previous["EMA12"] <= previous["EMA26"]
            and current["EMA12"] > current["EMA26"]
        )

    @staticmethod
    def bearish_crossover(previous: pd.Series, current: pd.Series) -> bool:
        """
        Returns True when EMA12 crosses below EMA26.
        """

        return (
            previous["EMA12"] >= previous["EMA26"]
            and current["EMA12"] < current["EMA26"]
        )

    @staticmethod
    def exit_long(rsi: float, exit_level: float = 50) -> bool:
        """
        Exit a long trade when RSI reaches the exit level.
        """
        return rsi >= exit_level

    @staticmethod
    def exit_short(rsi: float, exit_level: float = 50) -> bool:
        """
        Exit a short trade when RSI falls to the exit level.
        """
        return rsi <= exit_level