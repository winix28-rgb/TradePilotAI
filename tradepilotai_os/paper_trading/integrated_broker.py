"""Paper broker wrapper that synchronizes successful executions into the paper portfolio engine."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.broker.base import ExecutionResult
from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.risk.risk_engine import RiskAssessment

from .engine import PaperPortfolioEngine


class IntegratedPaperBroker:
    """Delegate execution to PaperBroker and mirror state into PaperPortfolioEngine."""

    def __init__(self, broker: PaperBroker, portfolio_engine: PaperPortfolioEngine) -> None:
        self._broker = broker
        self._portfolio_engine = portfolio_engine
        self._execution_context: dict[str, Any] = {}

    def prepare_execution(
        self,
        *,
        strategy_id: str = "",
        strategy_name: str,
        decision_id: str | None = None,
        decision: str | None = None,
        reason: str,
        risk_assessment: RiskAssessment | None,
    ) -> None:
        resolved_decision_id = decision_id if decision_id is not None else decision
        self._execution_context = {
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "decision_id": resolved_decision_id,
            "reason": reason,
            "risk_assessment": risk_assessment,
        }

    def execute(self, trade: Any) -> ExecutionResult:
        result = self._broker.execute(trade)
        if result.success:
            self._portfolio_engine.sync_execution(
                trade=trade,
                execution_result=result,
                strategy_id=str(self._execution_context.get("strategy_id", "")),
                strategy_name=str(self._execution_context.get("strategy_name", "Unknown")),
                decision_id=str(self._execution_context.get("decision_id", "WATCH")),
                reason=str(self._execution_context.get("reason", "Approved trade")),
                risk_assessment=self._execution_context.get("risk_assessment"),
            )
        self._execution_context = {}
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._broker, name)