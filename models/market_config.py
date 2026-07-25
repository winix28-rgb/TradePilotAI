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

    def __post_init__(self):

        if not self.ticker:
            raise ValueError(
                "ticker cannot be empty"
            )

        if not self.exchange:
            raise ValueError(
                "exchange cannot be empty"
            )

        if not self.timeframe:
            raise ValueError(
                "timeframe cannot be empty"
            )

        if not self.start_date:
            raise ValueError(
                "start_date cannot be empty"
            )

        if not self.end_date:
            raise ValueError(
                "end_date cannot be empty"
            )