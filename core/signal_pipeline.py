"""
===========================================================
TradePilotAI
Signal Pipeline
===========================================================

Moves strategy signals through risk approval.

Version 1:
- Accept signal
- Apply risk checks
- Return approved/rejected decision

No order execution.
"""

from __future__ import annotations



class SignalPipeline:
    """
    Handles signal approval workflow.
    """


    def __init__(
        self,
        risk_gateway,
    ) -> None:

        self.risk_gateway = risk_gateway



    def process(
        self,
        signal,
    ):
        """
        Process a strategy signal.

        Returns:
            Approved signal
            or
            None if rejected
        """


        if signal is None:

            return None


        approved = (
            self.risk_gateway.approve(
                signal
            )
        )


        if not approved:

            return None


        return signal