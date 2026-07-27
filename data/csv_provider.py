"""
===========================================================
TradePilotAI
CSV Data Provider
===========================================================

Loads historical market data from CSV files and converts it
into the internal HistoricalData format.
"""

from __future__ import annotations

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData

from data.data_loader import DataLoader

from data.data_provider import DataProvider


class CSVProvider(DataProvider):
    """
    CSV market data provider.
    """


    def load(
        self,
        symbol: str,
        start_date: str = "",
        end_date: str = "",
    ) -> HistoricalData:
        """
        Load market data from CSV.

        The symbol parameter represents the filename.
        """


        dataframe = DataLoader.load_csv(
            symbol
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