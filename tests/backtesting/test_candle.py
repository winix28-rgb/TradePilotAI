"""
===========================================================
TradePilotAI
Candle Tests
===========================================================
"""

from datetime import datetime

import pytest

from backtesting.candle import Candle


def test_candle_properties() -> None:
    """
    Verify candle helper properties.
    """

    candle = Candle(
        timestamp=datetime(2025, 1, 1),
        open=100,
        high=110,
        low=95,
        close=108,
        volume=100000,
    )

    assert candle.range == 15
    assert candle.body == 8
    assert candle.bullish is True
    assert candle.bearish is False


def test_bearish_candle() -> None:
    """
    Verify bearish candle detection.
    """

    candle = Candle(
        timestamp=datetime(2025, 1, 1),
        open=100,
        high=105,
        low=90,
        close=92,
        volume=50000,
    )

    assert candle.bullish is False
    assert candle.bearish is True


def test_invalid_high_low_raises_error() -> None:
    """
    High cannot be less than low.
    """

    with pytest.raises(ValueError):
        Candle(
            timestamp=datetime(2025, 1, 1),
            open=100,
            high=90,
            low=95,
            close=98,
            volume=1000,
        )


def test_invalid_open_raises_error() -> None:
    """
    Open must lie between low and high.
    """

    with pytest.raises(ValueError):
        Candle(
            timestamp=datetime(2025, 1, 1),
            open=120,
            high=110,
            low=90,
            close=100,
            volume=1000,
        )


def test_invalid_close_raises_error() -> None:
    """
    Close must lie between low and high.
    """

    with pytest.raises(ValueError):
        Candle(
            timestamp=datetime(2025, 1, 1),
            open=100,
            high=110,
            low=90,
            close=120,
            volume=1000,
        )


def test_negative_volume_raises_error() -> None:
    """
    Volume cannot be negative.
    """

    with pytest.raises(ValueError):
        Candle(
            timestamp=datetime(2025, 1, 1),
            open=100,
            high=110,
            low=90,
            close=100,
            volume=-1,
        )