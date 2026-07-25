"""
===========================================================
TradePilotAI
Strategy Base Class
===========================================================

Defines the interface that every trading strategy must
implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backtesting.historical_data import HistoricalData
from signals.trade_signal import TradeSignal


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    """

    @abstractmethod
    def generate_signal(
        self,
        symbol: str,
        historical_data: HistoricalData,
        index: int,
    ) -> TradeSignal | None:
        """
        Analyse market data and return a trading signal.

        Args:
            symbol:
                The instrument being analysed.

            historical_data:
                Historical OHLCV market data.

            index:
                The current candle index.

        Returns:
            TradeSignal when an action should be taken.
            None when no trade should occur.
        """
        raise NotImplementedError