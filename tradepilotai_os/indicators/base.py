"""Shared base classes for indicator components."""

from __future__ import annotations

from abc import ABC, abstractmethod

try:
    import pandas as pd
except ImportError:  # pragma: no cover - exercised when pandas is unavailable
    pd = None


class Indicator(ABC):
    """Common interface for reusable technical indicators."""

    name: str = "indicator"

    @classmethod
    @abstractmethod
    def calculate(cls, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Compute the indicator values for the supplied data."""

    @staticmethod
    def require_close_column(data: pd.DataFrame) -> None:
        """Validate that the dataframe contains the required close column."""

        if "Close" not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column.")
