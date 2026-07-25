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