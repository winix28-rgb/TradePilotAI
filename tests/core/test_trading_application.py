"""
===========================================================
TradePilotAI
Trading Application Tests
===========================================================
"""

from core.trading_application import (
    TradingApplication,
)



class FakeSignal:

    symbol = "RR.L"

    action = "BUY"

    entry_price = 8.50

    stop_loss = 8.10

    strategy = "RSI Mean Reversion"



class FakeBridge:


    def __init__(self):

        self.manager = None



    def submit(
        self,
        signal,
        quantity,
    ):

        from core.trade_approval import TradeApproval

        trade = TradeApproval(

            symbol=signal.symbol,

            action=signal.action,

            quantity=quantity,

            entry_price=signal.entry_price,

            stop_loss=signal.stop_loss,

            strategy=signal.strategy,

        )

        self.manager.add(trade)

        return trade



class FakeManager:


    def __init__(self):

        self.trade = None



    def add(
        self,
        trade,
    ):

        self.trade = trade



    def approve(
        self,
        symbol,
    ):

        self.trade.approve()

        return self.trade



    def reject(
        self,
        symbol,
    ):

        self.trade.reject()

        return self.trade



class FakeOrderFactory:


    def create_order(
        self,
        trade,
        quantity,
    ):

        return "ORDER"



class FakeExecution:


    def execute(
        self,
        order,
    ):

        return "EXECUTED"



def test_application_approval_flow():

    manager = FakeManager()


    app = TradingApplication(

        FakeBridge(),

        manager,

        FakeOrderFactory(),

        FakeExecution(),

    )


    app.signal_bridge.manager = manager


    result = app.receive_signal(
        FakeSignal()
    )


    assert result.symbol == "RR.L"


    execution = app.approve_trade(
        "RR.L"
    )


    assert execution == "EXECUTED"