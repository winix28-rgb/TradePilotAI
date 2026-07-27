"""
===========================================================
TradePilotAI
Market Data Service
===========================================================

Provides a single interface for retrieving historical
market data from different providers.
"""

from __future__ import annotations

from data.csv_provider import CSVProvider
from data.data_provider import DataProvider
from data.yahoo_provider import YahooProvider


class MarketDataService:
    """
    Central access point for market data.
    """


    def __init__(self) -> None:

        self._providers: dict[str, DataProvider] = {

            "yahoo": YahooProvider(),

            "csv": CSVProvider(),

        }


    def register_provider(
        self,
        name: str,
        provider: DataProvider,
    ) -> None:
        """
        Register a new data provider.

        Example:
            IG Markets provider
        """

        self._providers[name] = provider



    def get_history(
        self,
        provider: str,
        symbol: str,
        start_date: str = "2015-01-01",
        end_date: str = "2025-12-31",
    ):
        """
        Retrieve historical market data.
        """

        if provider not in self._providers:

            raise ValueError(
                f"Unknown data provider: {provider}"
            )


        return self._providers[provider].load(

            symbol=symbol,

            start_date=start_date,

            end_date=end_date,

        )