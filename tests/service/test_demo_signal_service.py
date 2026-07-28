"""
===========================================================
TradePilotAI
Demo Signal Service Tests
===========================================================
"""

from services.demo_signal_service import (
    DemoSignalService,
)


from core.approval_manager import (
    ApprovalManager,
)


from core.signal_bridge import (
    SignalBridge,
)



def test_demo_signal_service_creates_trade():

    approval_manager = ApprovalManager()


    bridge = SignalBridge(
        approval_manager
    )


    service = DemoSignalService(
        bridge
    )


    trade = (
        service.create_demo_trade()
    )


    assert trade.symbol == "RR.L"

    assert trade.action == "BUY"


    pending = (
        approval_manager.pending()
    )


    assert len(pending) == 1