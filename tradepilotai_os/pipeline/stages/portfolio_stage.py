"""Portfolio pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class PortfolioStage(PipelineStage):
    """Wrap a portfolio manager as a pipeline stage."""

    def __init__(self, portfolio_service: Any) -> None:
        self._portfolio_service = portfolio_service

    def execute(self, context: PipelineContext) -> None:
        """Update portfolio state from the current context."""

        approved_trades = context.get("approved_trades", [])
        for trade in approved_trades:
            self._portfolio_service.add_trade(trade)

        context.set("portfolio_state", self._portfolio_service.state)
