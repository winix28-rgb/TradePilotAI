"""
===========================================================
FTSE Quant Trader V2
Signal Model
===========================================================

Represents a trading signal.
"""

from dataclasses import dataclass


@dataclass
class Signal:
    """
    Represents a BUY or SELL signal.
    """

    ticker: str
    signal_type: str
    entry_price: float
    stop_loss: float
    rsi: float
    ema12: float
    ema26: float