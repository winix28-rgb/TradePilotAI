"""
===========================================================
TradePilotAI
Execution Router
===========================================================

Routes approved orders to the correct execution mode.

Modes:

DRY_RUN
- Logs order
- No execution

PAPER
- Uses PaperBroker

DEMO
- Uses IG Broker
"""

from __future__ import annotations



class ExecutionRouter:
    """
    Controls order execution destination.
    """


    def __init__(
        self,
        broker,
        mode: str = "DRY_RUN",
    ) -> None:

        self.broker = broker

        self.mode = mode.upper()



    def execute(
        self,
        order,
    ):
        """
        Execute or simulate an order.
        """


        if self.mode == "DRY_RUN":

            return {
                "status": "DRY_RUN",
                "order": order,
            }



        if self.mode in (
            "PAPER",
            "DEMO",
        ):

            return self.broker.execute(
                order
            )



        raise ValueError(
            f"Unsupported execution mode: {self.mode}"
        )