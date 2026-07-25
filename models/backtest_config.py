"""
===========================================================
TradePilotAI
Backtest Configuration
===========================================================

Configuration values used by the backtesting engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BacktestConfig:
    """
    Configuration for the backtest engine.
    """

    starting_cash: float = 100_000.0

    benchmark: str = "FTSE100"

    reinvest_profits: bool = True

    allow_fractional_shares: bool = False