"""
===========================================================
TradePilotAI
Live Market Service
===========================================================

Provides live market data from IG.
"""

from __future__ import annotations

import pandas as pd



class LiveMarketService:
    """
    Converts IG market data into strategy-ready format.
    """


    def __init__(
        self,
        ig_client,
    ) -> None:

        self._client = ig_client



    def get_latest_prices(
        self,
        epic: str,
        resolution="MINUTE",
    ) -> pd.DataFrame:
        """
        Retrieve latest market prices.
        """


        candles = self._client.get_market_prices(

            epic,

            resolution,

        )


        rows = []


        for candle in candles:

            rows.append(

                {
                    "Date":
                        candle.name,

                    "Open":
                        candle["openPrice"]["ask"],

                    "High":
                        candle["highPrice"]["ask"],

                    "Low":
                        candle["lowPrice"]["ask"],

                    "Close":
                        candle["closePrice"]["ask"],

                    "Volume":
                        candle.get(
                            "lastTradedVolume",
                            0,
                        ),

                }

            )


        dataframe = pd.DataFrame(
            rows
        )


        if not dataframe.empty:

            dataframe.set_index(
                "Date",
                inplace=True,
            )


        return dataframe