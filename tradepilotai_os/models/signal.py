"""Signal model for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Signal:
    """Represents a detected trading signal for a symbol."""

    ticker: str
    signal_type: str
    entry_price: float
    stop_loss: float
    rsi: float
    ema12: float
    ema26: float
