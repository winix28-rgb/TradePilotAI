"""Relative Strength Index indicator component."""

from __future__ import annotations

try:
    import pandas as pd
except ImportError:  # pragma: no cover - exercised when pandas is unavailable
    pd = None

from .base import Indicator


class RSI(Indicator):
    """Calculate the Relative Strength Index for a price series."""

    name = "rsi"

    @classmethod
    def calculate(cls, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Compute the RSI for the close series.

        Parameters
        ----------
        data:
            A dataframe that contains a Close column.
        period:
            The RSI period to use.
        """

        cls.require_close_column(data)

        delta = data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        average_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        average_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

        rs = average_gain / average_loss
        return 100 - (100 / (1 + rs))
