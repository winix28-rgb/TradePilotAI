"""
===========================================================
TradePilotAI OS
Yahoo Finance Market Data Provider
===========================================================

Provides live and historical market data using yfinance.
"""

from __future__ import annotations

import yfinance as yf

from tradepilotai_os.market_data.provider import MarketDataProvider
from tradepilotai_os.symbols import SymbolMapper


class YahooMarketDataProvider(MarketDataProvider):

    def __init__(self):

        self.symbols = SymbolMapper()

    def history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ):

        yahoo_symbol = self._resolve_symbol(symbol)

        data = yf.download(
            yahoo_symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )

        if data is None or data.empty:
            return data

        data = data.dropna(how="all")

        # yfinance can return a trailing row with NaN close values.
        # Remove rows without a valid close so downstream signal logic reads a valid latest candle.
        if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:
            level0 = list(data.columns.get_level_values(0))
            if "Close" in level0:
                close_frame = data.xs("Close", axis=1, level=0)
                data = data.loc[close_frame.notna().any(axis=1)]
        elif "Close" in data.columns:
            data = data.loc[data["Close"].notna()]

        return data

    def quote(
        self,
        symbol: str,
    ):

        yahoo_symbol = self._resolve_symbol(symbol)

        ticker = yf.Ticker(yahoo_symbol)

        info = ticker.fast_info

        return {
            "symbol": symbol,
            "provider_symbol": yahoo_symbol,
            "price": info.get("lastPrice"),
            "open": info.get("open"),
            "high": info.get("dayHigh"),
            "low": info.get("dayLow"),
            "volume": info.get("lastVolume"),
            "currency": info.get("currency"),
        }

    def _resolve_symbol(self, symbol: str) -> str:
        try:
            return self.symbols.yahoo(symbol)
        except KeyError:
            return symbol

    def connected(self) -> bool:

        try:

            ticker = yf.Ticker("RR.L")

            ticker.fast_info

            return True

        except Exception:

            return False