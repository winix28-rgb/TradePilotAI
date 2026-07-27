"""
===========================================================
TradePilotAI
EMA Indicator Tests
===========================================================
"""

from indicators.ema import calculate_ema


def test_ema_returns_same_length():

    prices = [
        100,
        102,
        104,
        106,
    ]

    result = calculate_ema(
        prices,
        period=3,
    )

    assert len(result) == len(prices)


def test_ema_first_value_equals_first_price():

    prices = [
        100,
        105,
        110,
    ]

    result = calculate_ema(
        prices,
        period=3,
    )

    assert result[0] == 100


def test_ema_moves_towards_latest_price():

    prices = [
        100,
        110,
        120,
    ]

    result = calculate_ema(
        prices,
        period=3,
    )

    assert result[-1] > result[0]