"""
===========================================================
TradePilotAI
Historical Data
===========================================================

Represents a collection of historical market candles.
"""

from collections.abc import Iterator

from backtesting.candle import Candle


class HistoricalData:
    """
    Container for historical market data.
    """

    def __init__(self, candles: list[Candle]):

        if not candles:
            raise ValueError(
                "HistoricalData requires at least one candle."
            )

        self._candles = candles

    @property
    def candles(self) -> list[Candle]:
        """
        Return a copy of the candle list.
        """
        return self._candles.copy()

    @property
    def first(self) -> Candle:
        """
        First candle.
        """
        return self._candles[0]

    @property
    def last(self) -> Candle:
        """
        Last candle.
        """
        return self._candles[-1]

    @property
    def length(self) -> int:
        """
        Number of candles.
        """
        return len(self._candles)

    def __len__(self) -> int:
        return len(self._candles)

    def __iter__(self) -> Iterator[Candle]:
        return iter(self._candles)

    def __getitem__(self, index: int) -> Candle:
        return self._candles[index]