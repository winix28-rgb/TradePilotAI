"""
===========================================================
TradePilotAI
Signal Bridge
===========================================================

Converts trading signals into approval requests.
"""

from __future__ import annotations

from core.trade_approval import TradeApproval



class SignalBridge:
    """
    Converts strategy signals into dashboard approvals.
    """


    def __init__(
        self,
        approval_manager,
    ) -> None:

        self.approval_manager = approval_manager



    def submit(
        self,
        signal,
        quantity: int = 1,
    ):
        """
        Convert signal into approval request.
        """


        if signal is None:

            return None


        approval = TradeApproval(

            symbol=signal.symbol,

            action=signal.action,

            quantity=quantity,

            entry_price=signal.entry_price,

            stop_loss=signal.stop_loss,

            strategy=signal.strategy,

        )


        self.approval_manager.add(
            approval
        )


        return approval