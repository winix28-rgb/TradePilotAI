"""
===========================================================
TradePilotAI
Equity Point
===========================================================

Represents the portfolio equity at a specific point in time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EquityPoint:
    """
    A snapshot of portfolio equity.
    """

    timestamp: datetime
    equity: float