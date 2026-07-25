"""
===========================================================
TradePilotAI
Strategy Configuration
===========================================================

Configuration values used by trading strategies.

The default values represent the production RSI Mean
Reversion strategy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class StrategyConfig:
    """
    Configuration for trading strategies.
    """

    buy_rsi: int = 30

    exit_rsi: int = 50

    ema_fast: int = 12

    ema_slow: int = 26