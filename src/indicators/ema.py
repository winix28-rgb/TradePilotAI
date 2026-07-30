"""
===========================================================
FTSE Quant Trader V2
EMA Indicator
===========================================================

This module calculates Exponential Moving Averages (EMA).
"""

import pandas as pd


class EMA:
    """
    EMA calculator.
    """

    @staticmethod
    def calculate(data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate an Exponential Moving Average.

        Parameters
        ----------
        data : pandas.DataFrame
            Market data containing a Close column.

        period : int
            EMA period (e.g. 12 or 26).

        Returns
        -------
        pandas.Series
            EMA values.
        """

        if "Close" not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column.")

        return data["Close"].ewm(
            span=period,
            adjust=False
        ).mean()