"""IG broker adapter skeleton for the TradePilotAI OS."""

from __future__ import annotations

from .base import BrokerInterface, ExecutionResult
from tradepilotai_os.models.trade import Trade


class IGBrokerAdapter(BrokerInterface):
    """Skeleton adapter for a future IG integration."""

    def execute(self, trade: Trade) -> ExecutionResult:
        return ExecutionResult(success=False, message="IG integration not yet connected.", trade=trade)
