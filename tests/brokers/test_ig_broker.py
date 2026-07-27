"""
===========================================================
TradePilotAI
IG Broker Tests
===========================================================
"""

from datetime import datetime

import pytest

from brokers.ig_broker import IGBroker

from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder

from signals.signal_types import SignalType



class FakeIGClient:
    """
    Fake IG client for testing.
    """

    def __init__(self):

        self.open_called = False

        self.close_called = False

        self.closed_deal = None


    def open_position(
        self,
        epic: str,
        direction: str,
        size: float,
        stop_distance=None,
        limit_distance=None,
    ):

        self.open_called = True

        return {
            "dealId": "ABC123"
        }


    def close_position(
        self,
        deal_id: str,
    ):

        self.close_called = True

        self.closed_deal = deal_id



def create_buy_order():

    return TradeOrder(

        symbol="RR.L",

        action=SignalType.BUY,

        quantity=10,

        price=100,

        stop_loss=95,

        take_profit=110,

        strategy="RSI",

        timestamp=datetime.now(),

    )



def create_sell_order():

    return TradeOrder(

        symbol="RR.L",

        action=SignalType.SELL,

        quantity=10,

        price=110,

        stop_loss=95,

        take_profit=120,

        strategy="RSI",

        timestamp=datetime.now(),

    )



def test_buy_order_calls_ig():

    client = FakeIGClient()

    broker = IGBroker(client)


    broker.execute(
        create_buy_order()
    )


    assert client.open_called is True



def test_sell_order_calls_close():

    client = FakeIGClient()

    broker = IGBroker(client)


    # Open the position first so the broker
    # has the IG deal reference

    position = broker.execute(
        create_buy_order()
    )


    result = broker.execute(
        create_sell_order(),
        position,
    )


    assert client.close_called is True

    assert client.closed_deal == "ABC123"

    assert isinstance(
        result,
        Trade,
    )



def test_sell_without_position_fails():

    client = FakeIGClient()

    broker = IGBroker(client)


    with pytest.raises(ValueError):

        broker.execute(
            create_sell_order()
        )



def test_buy_returns_position():

    client = FakeIGClient()

    broker = IGBroker(client)


    result = broker.execute(
        create_buy_order()
    )


    assert isinstance(
        result,
        Position,
    )