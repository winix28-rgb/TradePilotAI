"""
===========================================================
FTSE Quant Trader V2
RSI Indicator
===========================================================

Calculates the Relative Strength Index (RSI).
"""

import pandas as pd


class RSI:
    """
    RSI calculator.
    """

    @staticmethod
    def calculate(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate the Relative Strength Index.

        Parameters
        ----------
        data : pandas.DataFrame
            Market data containing a Close column.

        period : int
            RSI calculation period.

        Returns
        -------
        pandas.Series
            RSI values.
        """

        if "Close" not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column.")

        delta = data["Close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        average_gain = gain.ewm(
            alpha=1 / period,
            adjust=False
        ).mean()

        average_loss = loss.ewm(
            alpha=1 / period,
            adjust=False
        ).mean()

        rs = average_gain / average_loss

        rsi = 100 - (100 / (1 + rs))

        return rsi