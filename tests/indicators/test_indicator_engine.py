"""
===========================================================
TradePilotAI
Indicator Engine Tests
===========================================================
"""

from datetime import datetime

from backtesting.candle import Candle

from indicators.indicator_engine import IndicatorEngine


def create_candles():

    return [
        Candle(
            timestamp=datetime(2025, 1, i + 1),
            open=100 + i,
            high=102 + i,
            low=99 + i,
            close=101 + i,
            volume=1000,
        )
        for i in range(30)
    ]


def test_indicator_engine_returns_same_length():

    candles = create_candles()

    engine = IndicatorEngine()

    result = engine.calculate(
        candles
    )

    assert len(result) == len(candles)


def test_indicator_engine_contains_indicators():

    candles = create_candles()

    engine = IndicatorEngine()

    result = engine.calculate(
        candles
    )

    bar = result[-1]

    assert "RSI" in bar
    assert "EMA12" in bar
    assert "EMA26" in bar


def test_indicator_engine_values_are_numeric():

    candles = create_candles()

    engine = IndicatorEngine()

    result = engine.calculate(
        candles
    )

    bar = result[-1]

    assert isinstance(
        bar["RSI"],
        float,
    )

    assert isinstance(
        bar["EMA12"],
        float,
    )

    assert isinstance(
        bar["EMA26"],
        float,
    )