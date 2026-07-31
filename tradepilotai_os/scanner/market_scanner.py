"""
===========================================================
TradePilotAI OS
Market Scanner
===========================================================
"""

from __future__ import annotations

from typing import Sequence

from tradepilotai_os.market_data import YahooMarketDataProvider


class MarketScanner:
    """
    Produces a live watchlist with current market data.
    """

    def __init__(
        self,
        symbols: Sequence[str] | None = None,
    ):

        self.provider = YahooMarketDataProvider()

        self._symbols = list(
            symbols or
            [
                "RR",
                "LLOY",
                "TSCO",
                "MKS",
                "BARC",
                "BP",
                "SHEL",
                "VOD",
                "AZN",
                "NG",
                "AAPL",
                "TSLA",
            ]
        )

    def get_watchlist(self) -> list[str]:

        return list(self._symbols)

    def scan(self) -> list[dict]:

        opportunities = []

        for symbol in self._symbols:

            try:

                quote = self.provider.quote(symbol)

                opportunities.append(quote)

            except Exception:

                continue

        return opportunities