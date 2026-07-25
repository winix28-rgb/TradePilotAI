"""
===========================================================
TradePilotAI
Market Configuration
===========================================================

Configuration values describing the market and
instrument to trade.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MarketConfig:
    """
    Configuration for market data.
    """

    ticker: str = "RR.L"

    exchange: str = "LSE"

    timeframe: str = "1d"

    start_date: str = "2015-01-01"

    end_date: str = "2025-12-31"