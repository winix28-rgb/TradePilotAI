"""
===========================================================
TradePilotAI
IG Markets Data Provider
===========================================================

Converts IG Markets historical price data into the internal
HistoricalData format.
"""

from __future__ import annotations

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData

from brokers.ig_client import IGClient

from data.data_provider import DataProvider


class IGProvider(DataProvider):
    """
    IG Markets historical data provider.
    """


    def __init__(
        self,
        client: IGClient,
    ) -> None:

        self._client = client



    def load(
        self,
        symbol: str,
        start_date: str = "2015-01-01",
        end_date: str = "2025-12-31",
    ) -> HistoricalData:
        """
        Load historical prices from IG Markets.

        The symbol represents the IG epic.
        """


        prices = self._client.get_historical_prices(

            epic=symbol,

            start_date=start_date,

            end_date=end_date,

        )


        candles: list[Candle] = []


        for price in prices:

            candles.append(

                Candle(

                    timestamp=self._convert_timestamp(
                        price["timestamp"]
                    ),

                    open=float(
                        price["open"]
                    ),

                    high=float(
                        price["high"]
                    ),

                    low=float(
                        price["low"]
                    ),

                    close=float(
                        price["close"]
                    ),

                    volume=float(
                        price.get(
                            "volume",
                            0
                        )
                    ),

                )

            )


        return HistoricalData(
            candles
        )



    @staticmethod
    def _convert_timestamp(
        value,
    ) -> datetime:
        """
        Convert supported timestamp formats.
        """

        if isinstance(
            value,
            datetime,
        ):

            return value


        return datetime.fromisoformat(
            value
        )