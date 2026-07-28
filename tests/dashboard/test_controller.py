"""
===========================================================
TradePilotAI
Dashboard Controller Tests
===========================================================
"""

from dashboard.controller import DashboardController



class FakeApprovalManager:


    def pending(self):

        return [
            "RR.L"
        ]



class FakeApplication:


    def __init__(self):

        self.approval_manager = (
            FakeApprovalManager()
        )


    def approve_trade(
        self,
        symbol,
    ):

        return (
            f"Approved {symbol}"
        )


    def reject_trade(
        self,
        symbol,
    ):

        return (
            f"Rejected {symbol}"
        )



def test_get_pending_trades():

    controller = DashboardController(
        FakeApplication()
    )


    result = (
        controller
        .get_pending_trades()
    )


    assert result == [
        "RR.L"
    ]



def test_approve_trade():

    controller = DashboardController(
        FakeApplication()
    )


    result = (
        controller
        .approve_trade(
            "RR.L"
        )
    )


    assert result == "Approved RR.L"



def test_reject_trade():

    controller = DashboardController(
        FakeApplication()
    )


    result = (
        controller
        .reject_trade(
            "RR.L"
        )
    )


    assert result == "Rejected RR.L"