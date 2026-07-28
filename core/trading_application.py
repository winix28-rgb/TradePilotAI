"""
===========================================================
TradePilotAI
Trading Application
===========================================================

Coordinates the complete trading workflow.

Flow:

Signal
  |
Approval
  |
Execution
"""

from __future__ import annotations



class TradingApplication:
    """
    Main application coordinator.
    """


    def __init__(
        self,
        signal_bridge,
        approval_manager,
        order_factory,
        execution_router,
    ) -> None:

        self.signal_bridge = signal_bridge

        self.approval_manager = approval_manager

        self.order_factory = order_factory

        self.execution_router = execution_router



    def receive_signal(
        self,
        signal,
        quantity: int = 1,
    ):
        """
        Receive strategy signal.

        Sends it to approval queue.
        """


        return self.signal_bridge.submit(
            signal,
            quantity,
        )



    def approve_trade(
        self,
        symbol: str,
    ):

        approval = (
            self.approval_manager.approve(
                symbol
            )
        )


        if approval is None:

            return None


        order = (
            self.order_factory.create_order(
                approval,
                approval.quantity,
            )
        )


        return (
            self.execution_router.execute(
                order
            )
        )



    def reject_trade(
        self,
        symbol: str,
    ):

        return (
            self.approval_manager.reject(
                symbol
            )
        )