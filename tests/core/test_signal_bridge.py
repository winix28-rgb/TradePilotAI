"""
===========================================================
TradePilotAI
Signal Bridge Tests
===========================================================
"""

from core.signal_bridge import SignalBridge
from core.approval_manager import ApprovalManager



class FakeSignal:


    symbol = "RR.L"

    action = "BUY"

    entry_price = 8.50

    stop_loss = 8.10

    strategy = "RSI Mean Reversion"



def test_signal_creates_approval():

    manager = ApprovalManager()


    bridge = SignalBridge(
        manager
    )


    result = bridge.submit(
        FakeSignal()
    )


    assert result.symbol == "RR.L"

    assert result.status == "PENDING"



def test_signal_added_to_queue():

    manager = ApprovalManager()


    bridge = SignalBridge(
        manager
    )


    bridge.submit(
        FakeSignal()
    )


    pending = manager.pending()


    assert len(pending) == 1