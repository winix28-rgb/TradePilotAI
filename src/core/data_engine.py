"""
===========================================================
FTSE Quant Trader V2
Data Engine
===========================================================

This module is responsible for downloading market data.

Current Provider:
    Yahoo Finance

Future Providers:
    - IG Markets
    - CSV Files
    - TradingView Export
"""

import yfinance as yf


class DataEngine:
    """
    Downloads historical market data.
    """

    def __init__(self):
        print("Data Engine Initialised")

    def download_data(self, ticker, interval, period):
        """
        Download historical price data.

        Parameters
        ----------
        ticker : str
            Example: RR.L

        interval : str
            Example: 1h

        period : str
            Example: 180d
        """

        print()
        print("Downloading Market Data...")
        print("---------------------------")
        print(f"Ticker   : {ticker}")
        print(f"Interval : {interval}")
        print(f"Period   : {period}")
        print()

        try:

            data = yf.download(
                ticker,
                interval=interval,
                period=period,
                auto_adjust=True,
                progress=False,
            )

            if data.empty:

                print("No data returned.")

                return None

            # Flatten MultiIndex columns if required
            if data.columns.nlevels > 1:
                data.columns = data.columns.get_level_values(0)

            print(f"Downloaded {len(data)} candles")
            print()

            return data

        except Exception as error:

            print(f"Download Error: {error}")

            return None