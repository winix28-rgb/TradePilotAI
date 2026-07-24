"""
===========================================================
TradePilotAI
Position Sizer Tests
===========================================================
"""

from portfolio.position_sizer import PositionSizer


def test_maximum_risk():
    """
    Maximum risk should equal account size × risk percentage.
    """

    sizer = PositionSizer(
        account_size=100000,
        risk_per_trade=0.01,
    )

    assert sizer.maximum_risk == 1000


def test_position_size():
    """
    Position size should be calculated correctly.
    """

    sizer = PositionSizer(
        account_size=100000,
        risk_per_trade=0.01,
    )

    shares = sizer.calculate_position_size(
        entry_price=250,
        stop_price=245,
    )

    assert shares == 200


def test_zero_risk_returns_zero():
    """
    Zero stop distance should return zero shares.
    """

    sizer = PositionSizer(
        account_size=100000,
        risk_per_trade=0.01,
    )

    assert (
        sizer.calculate_position_size(
            entry_price=100,
            stop_price=100,
        )
        == 0
    )


def test_position_value():
    """
    Position value should equal shares × price.
    """

    sizer = PositionSizer(account_size=100000)

    assert sizer.position_value(
        shares=100,
        entry_price=250,
    ) == 25000