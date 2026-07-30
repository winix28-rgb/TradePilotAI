"""Market status model for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MarketStatus:
    """Represents the latest observed market status for a symbol."""

    ticker: str
    trend: str
    current_signal: str
    signal_age: int
    close: float
    ema12: float
    ema26: float
    rsi: float
