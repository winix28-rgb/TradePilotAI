"""
===========================================================
FTSE Quant Trader V2
Strategy State Model
===========================================================

Stores the current state of the trading strategy.
"""

from dataclasses import dataclass
from typing import Optional
from pandas import Timestamp


@dataclass
class StrategyState:
    """
    Holds the current state of the strategy.
    """

    # =========================================================
    # Strategy States
    # =========================================================

    IDLE = "IDLE"

    WATCHING_LONG = "WATCHING_LONG"
    READY_TO_BUY = "READY_TO_BUY"
    LONG = "LONG"

    WATCHING_SHORT = "WATCHING_SHORT"
    READY_TO_SELL = "READY_TO_SELL"
    SHORT = "SHORT"

    # =========================================================
    # Current Strategy State
    # =========================================================

    state: str = IDLE

    # =========================================================
    # Long Setup Information
    # =========================================================

    # Lowest Low while RSI is below 30
    lowest_low: Optional[float] = None

    # Number of candles since entering READY_TO_BUY
    setup_age: int = 0

    # =========================================================
    # Short Setup Information
    # =========================================================

    # Highest High while RSI is above 70
    highest_high: Optional[float] = None

    # =========================================================
    # Active Trade Information
    # =========================================================

    entry_price: Optional[float] = None

    stop_loss: Optional[float] = None

    # Candle index where the trade was opened
    entry_index: Optional[int] = None

    # Time the trade was opened
    entry_time: Optional[Timestamp] = None