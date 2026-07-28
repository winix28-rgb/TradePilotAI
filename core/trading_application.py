"""
===========================================================
TradePilotAI
Trading Application
===========================================================

Coordinates the complete trading workflow.

Flow:

Signal
  |
Approval Queue
  |
User Decision
  |
Order Creation
  |
Execution
  |
Trade Journal
"""

from __future__ import annotations



class TradingApplication:
    """
    Main application coordinator.

    Handles:
    - Receiving signals
    - Approval workflow
    - Order creation
    - Execution
    - Journal logging
    """



    def __init__(
        self,
        signal_bridge,
        approval_manager,
        order_factory,
        execution_router,
        journal=None,
    ) -> None:

        self.signal_bridge = signal_bridge

        self.approval_manager = approval_manager

        self.order_factory = order_factory

        self.execution_router = execution_router

        self.journal = journal



    def receive_signal(
        self,
        signal,
        quantity: int = 1,
    ):
        """
        Receive strategy signal
        and create approval request.
        """

        approval = (
            self.signal_bridge.submit(
                signal,
                quantity,
            )
        )


        if self.journal and approval:

            self.journal.record(

                "SIGNAL",

                signal.symbol,

                {
                    "action": signal.action,
                    "strategy": signal.strategy,
                    "entry_price": signal.entry_price,
                }

            )


        return approval



    def approve_trade(
        self,
        symbol: str,
    ):
        """
        Approve trade and execute.
        """

        approval = (
            self.approval_manager.approve(
                symbol
            )
        )


        if approval is None:

            return None



        if self.journal:

            self.journal.record(

                "APPROVED",

                symbol,

                {
                    "quantity": approval.quantity,
                    "entry_price": approval.entry_price,
                }

            )



        order = (
            self.order_factory.create_order(
                approval,
                approval.quantity,
            )
        )



        if self.journal:

            self.journal.record(

                "ORDER_CREATED",

                symbol,

                {
                    "order": str(order)
                }

            )



        result = (
            self.execution_router.execute(
                order
            )
        )



        if self.journal:

            self.journal.record(

                "EXECUTED",

                symbol,

                {
                    "result": str(result)
                }

            )


        return result



    def reject_trade(
        self,
        symbol: str,
    ):
        """
        Reject trade.
        """

        result = (
            self.approval_manager.reject(
                symbol
            )
        )


        if self.journal:

            self.journal.record(

                "REJECTED",

                symbol

            )


        return result