"""Broker pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class BrokerStage(PipelineStage):
    """Wrap a broker service as a pipeline stage."""

    def __init__(self, broker_service: Any) -> None:
        self._broker_service = broker_service

    def execute(self, context: PipelineContext) -> None:
        """Record broker execution output into the context."""

        approved_trades = context.get("approved_trades", [])
        executed_trades: list[Any] = []
        rejected_trades: list[Any] = []

        for trade in approved_trades:
            result = self._broker_service.execute(trade)
            if result.success:
                executed_trades.append(trade)
            else:
                rejected_trades.append(trade)

        context.set("executed_trades", executed_trades)
        context.set("broker_output", self._broker_service)

        summary = context.get("summary", {})
        summary["orders_executed"] = summary.get("orders_executed", 0) + len(executed_trades)
        summary["orders_rejected"] = summary.get("orders_rejected", 0) + len(rejected_trades)
        context.set("summary", summary)
