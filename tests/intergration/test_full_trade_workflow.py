"""
===========================================================
TradePilotAI
Full Trading Workflow Integration Test
===========================================================

Tests:

Signal
  |
Approval
  |
Execution
  |
Journal
"""

from core.application_factory import ApplicationFactory
from core.trade_approval import TradeApproval



class FakeSignal:

    symbol = "RR.L"

    action = "BUY"

    entry_price = 8.50

    stop_loss = 8.20

    strategy = "RSI Mean Reversion"



class FakeSignalBridge:

    def __init__(self):

        self.approval_manager = None


    def submit(
        self,
        signal,
        quantity=1,
    ):

        approval = TradeApproval(

            symbol=signal.symbol,

            action=signal.action,

            quantity=quantity,

            entry_price=signal.entry_price,

            stop_loss=signal.stop_loss,

            strategy=signal.strategy,

        )


        self.approval_manager.add(
            approval
        )


        return approval



class FakeOrderFactory:

    def create_order(
        self,
        approval,
        quantity,
    ):

        return {
            "symbol": approval.symbol,
            "action": approval.action,
            "quantity": quantity,
        }



class FakeExecutionRouter:

    def execute(
        self,
        order,
    ):

        return {
            "status": "EXECUTED",
            "order": order,
        }



def test_complete_trade_workflow():

    signal_bridge = FakeSignalBridge()


    services = ApplicationFactory.create(

        signal_bridge,

        FakeOrderFactory(),

        FakeExecutionRouter(),

    )


    signal_bridge.approval_manager = (
        services["approval_manager"]
    )


    app = services["application"]



    approval = app.receive_signal(

        FakeSignal()

    )


    assert approval.symbol == "RR.L"



    result = app.approve_trade(

        "RR.L"

    )


    assert result["status"] == "EXECUTED"



    events = (
        services["journal"].events()
    )


    assert len(events) > 0