"""
===========================================================
TradePilotAI
Trade Order Tests
===========================================================
"""

from models.trade_order import TradeOrder
from signals.signal_types import SignalType


def test_order_value():
    """
    The order value should equal quantity × price.
    """

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=50,
        price=200,
    )

    assert order.value == 10000


def test_stop_loss_defaults_to_none():
    """
    Stop-loss should default to None.
    """

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=10,
        price=100,
    )

    assert order.stop_loss is None


def test_take_profit_defaults_to_none():
    """
    Take-profit should default to None.
    """

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=10,
        price=100,
    )

    assert order.take_profit is None


def test_strategy_defaults_to_empty_string():
    """
    Strategy should default to an empty string.
    """

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=10,
        price=100,
    )

    assert order.strategy == ""


def test_timestamp_is_created():
    """
    A timestamp should automatically be assigned.
    """

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=1,
        price=100,
    )

    assert order.timestamp is not None