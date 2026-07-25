"""
===========================================================
TradePilotAI
Historical Data Tests
===========================================================
"""

from datetime import datetime

import pytest

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData


def create_candle(price: float) -> Candle:
    """
    Create a simple test candle.
    """
    return Candle(
        timestamp=datetime(2025, 1, 1),
        open=price,
        high=price + 2,
        low=price - 2,
        close=price + 1,
        volume=1000,
    )


def test_historical_data_properties() -> None:
    """
    Verify HistoricalData properties.
    """

    data = HistoricalData(
        [
            create_candle(100),
            create_candle(110),
            create_candle(120),
        ]
    )

    assert data.length == 3
    assert len(data) == 3

    assert data.first.open == 100
    assert data.last.open == 120


def test_historical_data_iteration() -> None:
    """
    Verify HistoricalData is iterable.
    """

    data = HistoricalData(
        [
            create_candle(100),
            create_candle(110),
            create_candle(120),
        ]
    )

    prices = [candle.open for candle in data]

    assert prices == [100, 110, 120]


def test_historical_data_indexing() -> None:
    """
    Verify indexing support.
    """

    data = HistoricalData(
        [
            create_candle(100),
            create_candle(110),
            create_candle(120),
        ]
    )

    assert data[0].open == 100
    assert data[1].open == 110
    assert data[2].open == 120


def test_historical_data_returns_copy_of_candles() -> None:
    """
    Verify candles property returns a copy.
    """

    data = HistoricalData(
        [
            create_candle(100),
            create_candle(110),
        ]
    )

    candles = data.candles
    candles.append(create_candle(120))

    assert data.length == 2


def test_empty_historical_data_raises_error() -> None:
    """
    Verify an empty candle list is rejected.
    """

    with pytest.raises(ValueError):
        HistoricalData([])