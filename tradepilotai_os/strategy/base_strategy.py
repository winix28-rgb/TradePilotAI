"""
===========================================================
TradePilotAI OS
Base Strategy
===========================================================

Every trading strategy must inherit from this class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from tradepilotai_os.models.trade_signal import TradeSignal


class BaseStrategy(ABC):

    @abstractmethod
    def evaluate(
        self,
        symbol: str,
        data,
    ) -> TradeSignal:
        """
        Analyse market data and return a TradeSignal.
        """
        raise NotImplementedError