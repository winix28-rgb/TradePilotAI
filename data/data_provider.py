"""
===========================================================
TradePilotAI
Data Provider Interface
===========================================================

Defines the contract all market data providers must follow.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backtesting.historical_data import HistoricalData


class DataProvider(ABC):
    """
    Abstract market data provider.
    """


    @abstractmethod
    def load(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> HistoricalData:
        """
        Load historical market data.
        """

        raise NotImplementedError