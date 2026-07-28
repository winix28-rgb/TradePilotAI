"""
===========================================================
TradePilotAI
Trade Approval Workflow
===========================================================

Manages human approval before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime



@dataclass
class TradeApproval:

    symbol: str

    action: str

    quantity: int

    entry_price: float

    stop_loss: float | None = None

    strategy: str | None = None

    status: str = "PENDING"

    created_at: datetime = (
        datetime.now()
    )


    def approve(self) -> None:
        """
        Approve trade.
        """

        self.status = "APPROVED"



    def reject(self) -> None:
        """
        Reject trade.
        """

        self.status = "REJECTED"



    @property
    def is_pending(self) -> bool:

        return self.status == "PENDING"



    @property
    def is_approved(self) -> bool:

        return self.status == "APPROVED"