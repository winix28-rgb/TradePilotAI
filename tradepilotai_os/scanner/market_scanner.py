"""Market scanner for the TradePilotAI OS."""

from __future__ import annotations

from typing import Sequence


class MarketScanner:
    """Identify instruments that should be analyzed.

    This component is responsible only for producing a list of
    symbols for downstream data collection. It does not calculate
    indicators, generate signals, or make trading decisions.
    """

    def __init__(self, symbols: Sequence[str] | None = None) -> None:
        self._symbols = list(symbols or [
            "RR.L",
            "LLOY.L",
            "TSCO.L",
            "MKS.L",
            "BARC.L",
            "BP.L",
            "SHEL.L",
            "VOD.L",
            "AZN.L",
            "NG.L",
        ])

    def get_watchlist(self) -> list[str]:
        """Return the list of symbols that require analysis."""

        return list(self._symbols)

    def set_symbols(self, symbols: Sequence[str]) -> None:
        """Replace the active watchlist with a new symbol sequence."""

        self._symbols = list(symbols)
