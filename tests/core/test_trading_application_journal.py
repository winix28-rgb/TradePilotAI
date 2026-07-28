"""
===========================================================
TradePilotAI
Trading Application Journal Tests
===========================================================
"""

from core.trading_application import TradingApplication
from core.trade_journal import TradeJournal



class FakeSignal:

    symbol = "RR.L"

    action = "BUY"

    entry_price = 8.50

    stop_loss = 8.10

    strategy = "RSI Mean Reversion"



class FakeBridge:


    def __init__(self, manager):

        self.manager = manager



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



def test_journal_records_full_trade_flow():

    journal = TradeJournal()

    manager = FakeManager()


    app = TradingApplication(

        FakeBridge(manager),

        manager,

        FakeOrderFactory(),

        FakeExecution(),

        journal,

    )


    app.receive_signal(
        FakeSignal()
    )


    app.approve_trade(
        "RR.L"
    )


    events = journal.events()


    event_types = [

        event["type"]

        for event in events

    ]


    assert "SIGNAL" in event_types

    assert "APPROVED" in event_types

    assert "ORDER_CREATED" in event_types

    assert "EXECUTED" in event_types