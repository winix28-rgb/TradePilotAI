"""Strategy interface for pluggable backtesting strategies."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from tradepilotai_os.models.trade_signal import TradeSignal

from .models import StrategyParameter


class BacktestStrategy(ABC):
    """Contract required by all pluggable strategy implementations."""

    strategy_id: str
    name: str
    asset_class: str
    primary_timeframe: str
    supported_timeframes: list[str]
    description: str
    indicators: list[str]

    @property
    @abstractmethod
    def parameters(self) -> list[StrategyParameter]:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, symbol: str, data: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_signal(self, symbol: str, context: dict[str, Any]) -> TradeSignal:
        raise NotImplementedError
