"""Exponential Moving Average indicator component."""

from __future__ import annotations

try:
    import pandas as pd
except ImportError:  # pragma: no cover - exercised when pandas is unavailable
    pd = None

from .base import Indicator


class EMA(Indicator):
    """Calculate Exponential Moving Averages for a price series."""

    name = "ema"

    @classmethod
    def calculate(cls, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Compute an EMA for the close series.

        Parameters
        ----------
        data:
            A dataframe that contains a Close column.
        period:
            The EMA period to use.
        """

        cls.require_close_column(data)
        return data["Close"].ewm(span=period, adjust=False).mean()
