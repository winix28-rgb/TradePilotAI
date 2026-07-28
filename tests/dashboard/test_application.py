"""
===========================================================
TradePilotAI
Dashboard Application Tests
===========================================================
"""

from dashboard.application import (
    DashboardApplication,
)



class FakeController:


    def get_pending_trades(self):

        return ["RR.L"]


    def approve_trade(
        self,
        symbol,
    ):

        return "APPROVED"



    def reject_trade(
        self,
        symbol,
    ):

        return "REJECTED"



class FakeTradingApplication:
    pass



def test_dashboard_application():

    app = DashboardApplication(
        FakeTradingApplication()
    )


    assert app.controller is not None