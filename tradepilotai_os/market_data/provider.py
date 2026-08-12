"""
===========================================================
TradePilotAI OS
Market Data Provider Interface
===========================================================

Every market data source must implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class MarketDataProvider(ABC):

    @abstractmethod
    def history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str | None = None,
    ):
        """
        Return historical OHLCV data.
        """
        raise NotImplementedError

    @abstractmethod
    def quote(
        self,
        symbol: str,
    ):
        """
        Return the latest market quote.
        """
        raise NotImplementedError

    @abstractmethod
    def connected(self) -> bool:
        """
        Returns True if provider is available.
        """
        raise NotImplementedError