"""
===========================================================
TradePilotAI OS
Trade Signal
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TradeSignal:

    symbol: str

    signal: str

    confidence: int

    price: float

    rsi: float

    ema12: float

    ema26: float

    stop_loss: float

    target: float

    reasons: list[str] = field(default_factory=list)

    def is_buy(self) -> bool:

        return self.signal == "BUY"

    def is_sell(self) -> bool:

        return self.signal == "SELL"

    def is_watch(self) -> bool:

        return self.signal == "WATCH"