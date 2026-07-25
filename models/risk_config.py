"""
===========================================================
TradePilotAI
Risk Configuration
===========================================================

Configuration values used by the risk management
components of the trading system.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RiskConfig:
    """
    Configuration for portfolio risk management.
    """

    risk_per_trade: float = 1.0

    max_positions: int = 10

    allow_short_positions: bool = False

    commission: float = 0.0

    slippage: float = 0.0

    def __post_init__(self):

        if self.risk_per_trade <= 0:
            raise ValueError(
                "risk_per_trade must be greater than zero"
            )

        if self.risk_per_trade > 100:
            raise ValueError(
                "risk_per_trade cannot exceed 100"
            )

        if self.max_positions < 1:
            raise ValueError(
                "max_positions must be at least 1"
            )

        if self.commission < 0:
            raise ValueError(
                "commission cannot be negative"
            )

        if self.slippage < 0:
            raise ValueError(
                "slippage cannot be negative"
            )