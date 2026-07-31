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

        return yf.download(
            yahoo_symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )

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