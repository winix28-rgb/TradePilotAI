"""
===========================================================
TradePilotAI
Yahoo Finance Data Provider
===========================================================

Loads historical market data from Yahoo Finance and converts
it into the internal HistoricalData format.
"""

from __future__ import annotations

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData

from data.data_loader import DataLoader

from data.data_provider import DataProvider


class YahooProvider(DataProvider):
    """
    Yahoo Finance market data provider.
    """


    def load(
        self,
        symbol: str,
        start_date: str = "2015-01-01",
        end_date: str = "2025-12-31",
    ) -> HistoricalData:
        """
        Load Yahoo Finance data.

        Returns:
            HistoricalData
        """


        dataframe = DataLoader.load_yahoo(
            ticker=symbol,
            start_date=start_date,
            end_date=end_date,
        )


        candles: list[Candle] = []


        for timestamp, row in dataframe.iterrows():

            candles.append(

                Candle(

                    timestamp=(
                        timestamp.to_pydatetime()
                        if hasattr(
                            timestamp,
                            "to_pydatetime"
                        )
                        else timestamp
                    ),

                    open=float(row["Open"]),

                    high=float(row["High"]),

                    low=float(row["Low"]),

                    close=float(row["Close"]),

                    volume=float(row["Volume"]),

                )

            )


        return HistoricalData(
            candles
        )