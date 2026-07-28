"""
===========================================================
TradePilotAI
Dashboard Controller
===========================================================

Connects dashboard actions to the trading application.
"""

from __future__ import annotations



class DashboardController:
    """
    Controls dashboard interaction with
    the trading application.
    """


    def __init__(
        self,
        application,
    ) -> None:

        self.application = application



    def get_pending_trades(self):
        """
        Return trades awaiting approval.
        """

        return (
            self.application
            .approval_manager
            .pending()
        )



    def approve_trade(
        self,
        symbol: str,
    ):

        """
        Approve and execute a trade.
        """

        return (
            self.application
            .approve_trade(
                symbol
            )
        )



    def reject_trade(
        self,
        symbol: str,
    ):

        """
        Reject a trade.
        """

        return (
            self.application
            .reject_trade(
                symbol
            )
        )