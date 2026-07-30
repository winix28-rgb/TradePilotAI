"""
===========================================================
FTSE Quant Trader V2
Trade Model
===========================================================

Represents a single trade from entry to exit.
"""

from dataclasses import dataclass
from typing import Optional

from pandas import Timestamp


@dataclass
class Trade:
    """
    Represents one completed (or open) trade.
    """

    ticker: str

    direction: str          # LONG or SHORT

    entry_time: Timestamp
    entry_price: float

    stop_loss: float

    exit_time: Optional[Timestamp] = None
    exit_price: Optional[float] = None

    exit_reason: Optional[str] = None

    profit: Optional[float] = None

    status: str = "OPEN"