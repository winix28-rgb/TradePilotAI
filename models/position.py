"""
===========================================================
TradePilotAI
Position Model
Version 3.0
===========================================================

Represents a currently open position.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    """
    Represents an open trading position.
    """

    ticker: str

    direction: str

    quantity: int

    entry_time: datetime

    entry_price: float

    stop_loss: float

    current_price: float = 0.0

    unrealised_profit: float = 0.0

    risk: float = 0.0

    is_open: bool = True