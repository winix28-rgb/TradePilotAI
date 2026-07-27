"""
===========================================================
TradePilotAI
Market Data Service
===========================================================

Provides market data from supported sources.
"""

from __future__ import annotations



class MarketDataService:
    """
    Unified market data interface.
    """


    def __init__(
        self,
        provider,
    ) -> None:

        self._provider = provider



    def get_prices(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ):

        return self._provider.get_historical_prices(

            symbol,

            start_date,

            end_date,

        )