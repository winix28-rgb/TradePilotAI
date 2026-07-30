"""
===========================================================
FTSE Quant Trader V2
Market Status Model
===========================================================

Represents the current state of a stock after analysis.
"""

from dataclasses import dataclass


@dataclass
class MarketStatus:
    """
    Stores the current market status for one stock.
    """

    ticker: str

    trend: str

    current_signal: str

    signal_age: int

    close: float

    ema12: float

    ema26: float

    rsi: float