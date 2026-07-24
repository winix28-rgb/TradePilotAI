"""
===========================================================
TradePilotAI
Paper Broker Tests
===========================================================
"""

from models.trade_order import TradeOrder
from signals.signal_types import SignalType


def test_execute_buy_order(broker, account):
    """
    Executing an order should create a position and
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