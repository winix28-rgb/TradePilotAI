"""Risk pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class RiskStage(PipelineStage):
    """Wrap a risk engine as a pipeline stage."""

    def __init__(self, risk_service: Any) -> None:
        self._risk_service = risk_service

    def execute(self, context: PipelineContext) -> None:
        """Attach risk assessments to the current strategy decisions."""

        trade_proposals = context.get("trade_proposals", [])
        if not trade_proposals:
            return

        approved_trades: list[Any] = []
        rejected_trades: list[Any] = []
        risk_assessments: list[Any] = []

        for trade in trade_proposals:
            assessment = self._risk_service.assess_trade(trade)
            risk_assessments.append(assessment)
            if assessment.permitted:
                approved_trades.append(trade)
            else:
                rejected_trades.append(trade)

        context.set("approved_trades", approved_trades)
        context.set("rejected_trades", rejected_trades)
        context.set("risk_assessments", risk_assessments)

        summary = context.get("summary", {})
        summary["orders_submitted"] = summary.get("orders_submitted", 0) + len(approved_trades)
        summary["orders_rejected"] = summary.get("orders_rejected", 0) + len(rejected_trades)
        context.set("summary", summary)
