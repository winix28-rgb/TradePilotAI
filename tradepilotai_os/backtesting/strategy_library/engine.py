"""Adapter that exposes a legacy-compatible evaluate API for BacktestEngine."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.models.trade_signal import TradeSignal

from .interface import BacktestStrategy


class StrategyLibraryEngine:
    """Adapter consumed by BacktestEngine in place of the legacy StrategyEngine."""

    def __init__(self, strategy: BacktestStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> BacktestStrategy:
        return self._strategy

    @property
    def primary_timeframe(self) -> str:
        return str(getattr(self._strategy, "primary_timeframe", ""))

    def evaluate(self, symbol: str, data: Any) -> TradeSignal:
        context = self._strategy.evaluate(symbol=symbol, data=data)
        return self._strategy.generate_signal(symbol=symbol, context=context)
