"""
===========================================================
TradePilotAI
Demo Signal Dashboard Flow Test
===========================================================

Tests:

Demo Signal
    |
Signal Bridge
    |
Approval Queue
    |
Dashboard Controller
"""

from services.demo_signal_generator import (
    DemoSignalGenerator,
)

from core.approval_manager import (
    ApprovalManager,
)

from core.signal_bridge import (
    SignalBridge,
)

from dashboard.controller import (
    DashboardController,
)



class FakeApplication:
    """
    Minimal application wrapper for dashboard testing.
    """

    def __init__(
        self,
        approval_manager,
    ):

        self.approval_manager = approval_manager



def test_demo_signal_reaches_dashboard_queue():

    approval_manager = ApprovalManager()


    signal_bridge = SignalBridge(

        approval_manager

    )


    generator = DemoSignalGenerator()


    signal = (
        generator.create_buy_signal()
    )


    approval = signal_bridge.submit(

        signal

    )


    assert approval.symbol == "RR.L"

    assert approval.action == "BUY"



    application = FakeApplication(

        approval_manager

    )


    controller = DashboardController(

        application

    )


    pending = (
        controller.get_pending_trades()
    )


    assert len(pending) == 1

    assert pending[0].symbol == "RR.L"