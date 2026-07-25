"""
===========================================================
TradePilotAI
Candle
===========================================================

Represents a single OHLCV market candle.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    """
    Represents a single market candle.
    """

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float

    def __post_init__(self) -> None:
        """
        Validate candle values.
        """

        if self.high < self.low:
            raise ValueError("High price cannot be less than low price.")

        if not self.low <= self.open <= self.high:
            raise ValueError("Open price must lie between low and high.")

        if not self.low <= self.close <= self.high:
            raise ValueError("Close price must lie between low and high.")

        if self.volume < 0:
            raise ValueError("Volume cannot be negative.")

    @property
    def range(self) -> float:
        """
        High minus low.
        """
        return self.high - self.low

    @property
    def body(self) -> float:
        """
        Absolute candle body.
        """
        return abs(self.close - self.open)

    @property
    def bullish(self) -> bool:
        """
        True if close > open.
        """
        return self.close > self.open

    @property
    def bearish(self) -> bool:
        """
        True if close < open.
        """
        return self.close < self.open