"""
===========================================================
TradePilotAI
Dashboard Application Container
===========================================================

Creates the dashboard trading application instance.
"""

from __future__ import annotations


from dashboard.controller import DashboardController


class DashboardApplication:
    """
    Provides dashboard access to trading services.
    """


    def __init__(
        self,
        trading_application,
    ):

        self.controller = DashboardController(
            trading_application
        )


    def pending_trades(self):

        return (
            self.controller
            .get_pending_trades()
        )


    def approve(
        self,
        symbol: str,
    ):

        return (
            self.controller
            .approve_trade(
                symbol
            )
        )


    def reject(
        self,
        symbol: str,
    ):

        return (
            self.controller
            .reject_trade(
                symbol
            )
        )