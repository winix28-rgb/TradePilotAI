"""
===========================================================
TradePilotAI
RSI Indicator Tests
===========================================================
"""

from indicators.rsi import calculate_rsi


def test_rsi_returns_same_length():

    prices = [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
    ]

    result = calculate_rsi(
        prices,
        period=14,
    )

    assert len(result) == len(prices)


def test_rsi_neutral_when_not_enough_data():

    prices = [
        100,
        101,
        102,
    ]

    result = calculate_rsi(
        prices,
        period=14,
    )

    assert result == [
        50.0,
        50.0,
        50.0,
    ]


def test_rsi_rises_when_prices_rise():

    prices = [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
    ]

    result = calculate_rsi(
        prices,
        period=14,
    )

    assert result[-1] > 50