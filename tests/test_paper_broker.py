"""
===========================================================
TradePilotAI
Paper Broker Tests
===========================================================
"""

from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder
from signals.signal_types import SignalType


def test_execute_buy_order(broker, account):
    """
    Executing a BUY order should create a position and
    withdraw the correct amount of cash.
    """

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=100,
        price=250,
        stop_loss=240,
        take_profit=280,
        strategy="RSI",
    )

    position = broker.execute(order)

    assert position.symbol == "RR.L"
    assert position.quantity == 100
    assert position.entry_price == 250

    assert account.cash == 75000


def test_execute_sell_order(broker, account):
    """
    Executing a SELL order should create a completed trade
    and deposit the sale proceeds.
    """

    position = Position(
        symbol="RR.L",
        quantity=100,
        entry_price=250,
        current_price=250,
        strategy="RSI",
    )

    sell_order = TradeOrder(
        symbol="RR.L",
        action=SignalType.SELL,
        quantity=100,
        price=275,
        strategy="RSI",
    )

    trade = broker.execute(sell_order, position)

    assert isinstance(trade, Trade)

    assert trade.symbol == "RR.L"
    assert trade.quantity == 100

    assert trade.entry_price == 250
    assert trade.exit_price == 275

    assert trade.cost == 25000
    assert trade.proceeds == 27500
    assert trade.profit == 2500

    #
    # Initial cash = £100,000
    # BUY cost would have reduced this to £75,000
    # SELL proceeds should increase it to £102,500
    #
    assert account.cash == 127500


def test_sell_requires_position(broker):
    """
    SELL orders must provide an existing Position.
    """

    sell_order = TradeOrder(
        symbol="RR.L",
        action=SignalType.SELL,
        quantity=100,
        price=275,
    )

    import pytest

    with pytest.raises(ValueError):
        broker.execute(sell_order)