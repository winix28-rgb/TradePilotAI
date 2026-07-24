"""
===========================================================
TradePilotAI
Strategy State Model
Version 3.0
===========================================================

Represents the current state of a trading strategy
for a single instrument.
"""

from dataclasses import dataclass
from enum import Enum, auto


class StrategyStatus(Enum):
    """
    Possible states of the trading strategy.
    """

    IDLE = auto()

    WATCHING_LONG = auto()

    READY_TO_BUY = auto()

    LONG = auto()

    WATCHING_SHORT = auto()

    READY_TO_SELL = auto()

    SHORT = auto()


@dataclass
class StrategyState:
    """
    Stores the current state of a strategy.
    """

    state: StrategyStatus = StrategyStatus.IDLE

    lowest_low: float | None = None
    highest_high: float | None = None

    entry_price: float | None = None
    stop_loss: float | None = None

    entry_index: int | None = None
    entry_time = None

    setup_age: int = 0