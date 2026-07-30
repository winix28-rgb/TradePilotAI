"""Strategy pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class StrategyStage(PipelineStage):
    """Wrap a strategy service as a pipeline stage."""

    def __init__(self, strategy_service: Any) -> None:
        self._strategy_service = strategy_service

    def execute(self, context: PipelineContext) -> None:
        """Populate the context with strategy decisions for the current signals."""

        signals = context.get("signals", [])
        symbol = context.get("symbol")
        if symbol is None:
            return

        trade_proposals: list[Any] = []
        for signal in signals:
            _, trades = self._strategy_service.evaluate_signal(symbol, signal)
            trade_proposals.extend(trades)

        context.set("trade_proposals", trade_proposals)
