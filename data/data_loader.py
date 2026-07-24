"""
===========================================================
TradePilotAI
Data Loader
Version 3.0
===========================================================

Loads historical market data from supported sources.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf


class DataLoader:
    """
    Handles loading historical market data.
    """

    @staticmethod
    def load_yahoo(
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Load historical price data from Yahoo Finance.

        Parameters
        ----------
        ticker : str
            Market symbol (e.g. RR.L)

        start_date : str
            Start date (YYYY-MM-DD)

        end_date : str
            End date (YYYY-MM-DD)

        Returns
        -------
        pandas.DataFrame
            Historical OHLCV price data.
        """

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            raise ValueError(f"No data returned for {ticker}")

        return data

    @staticmethod
    def load_csv(filename: str) -> pd.DataFrame:
        """
        Load market data from a CSV file.
        """

        data = pd.read_csv(
            filename,
            index_col=0,
            parse_dates=True,
        )

        return data