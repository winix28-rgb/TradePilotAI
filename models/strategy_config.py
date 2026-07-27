"""
===========================================================
TradePilotAI
Strategy Configuration
===========================================================

Configuration values used by trading strategies.
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

    rsi_period: int = 14

    ema_fast: int = 12

    ema_slow: int = 26


    def __post_init__(self):

        if not 0 <= self.buy_rsi <= 100:
            raise ValueError(
                "buy_rsi must be between 0 and 100"
            )


        if not 0 <= self.exit_rsi <= 100:
            raise ValueError(
                "exit_rsi must be between 0 and 100"
            )


        if self.rsi_period <= 0:
            raise ValueError(
                "rsi_period must be greater than zero"
            )


        if self.ema_fast <= 0:
            raise ValueError(
                "ema_fast must be greater than zero"
            )


        if self.ema_slow <= 0:
            raise ValueError(
                "ema_slow must be greater than zero"
            )


        if self.ema_fast >= self.ema_slow:
            raise ValueError(
                "ema_fast must be less than ema_slow"
            )