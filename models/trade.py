"""
===========================================================
TradePilotAI
Trade Model
Version 3.0
===========================================================

Represents a completed or open trade.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """
    Stores all information relating to a trade.
    """

    ticker: str

    direction: str

    entry_time: datetime | None = None
    entry_price: float | None = None

    stop_loss: float | None = None

    exit_time: datetime | None = None
    exit_price: float | None = None

    exit_reason: str = ""

    profit: float = 0.0

    quantity: int = 0

    risk: float = 0.0

    reward: float = 0.0

    status: str = "OPEN"