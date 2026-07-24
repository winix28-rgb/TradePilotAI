"""
===========================================================
TradePilotAI
Data Loader
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
        start_date: str = "2015-01-01",
        end_date: str = "2025-12-31",
    ) -> pd.DataFrame:
        """
        Load historical price data from Yahoo Finance.
        """

        print(f"Downloading {ticker}...")

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            raise ValueError(f"No data returned for {ticker}")

        # -------------------------------------------------
        # Flatten MultiIndex columns returned by newer
        # versions of yfinance.
        # -------------------------------------------------

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Keep only the columns we need
        data = data[["Open", "High", "Low", "Close", "Volume"]]

        print(f"Downloaded {len(data)} price bars")

        return data

    @staticmethod
    def load_csv(filename: str) -> pd.DataFrame:
        """
        Load market data from CSV.
        """

        return pd.read_csv(
            filename,
            index_col=0,
            parse_dates=True,
        )