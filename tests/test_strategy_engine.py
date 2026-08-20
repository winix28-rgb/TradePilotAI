"""
===========================================================
TradePilotAI OS
Strategy Engine Test
===========================================================

Tests the Strategy Engine using deterministic market data.

The test deliberately does NOT depend on Yahoo Finance being
available during the test run.

Yahoo Finance remains responsible for live/historical market
data in the application. This test verifies the strategy
engine itself.
"""

from __future__ import annotations

import pandas as pd

from tradepilotai_os.indicators.indicator_engine import (
    IndicatorEngine,
)
from tradepilotai_os.strategy.strategy_engine import (
    StrategyEngine,
)


def make_market_data() -> pd.DataFrame:
    """
    Create deterministic OHLCV data for strategy testing.

    Exactly 60 candles are generated.

    The data contains a gradual rise followed by a gradual
    decline so the indicator engine has sufficient history
    to calculate EMA and RSI values.
    """

    periods = 60

    dates = pd.date_range(
        start="2026-08-01 09:00",
        periods=periods,
        freq="1h",
    )

    prices: list[float] = []

    # -----------------------------------------------------
    # First 30 candles: gradual rise
    # -----------------------------------------------------

    for index in range(30):
        prices.append(
            10.00 + (index * 0.02)
        )

    # -----------------------------------------------------
    # Last 30 candles: gradual decline
    # -----------------------------------------------------

    for index in range(30):
        prices.append(
            10.60 - (index * 0.02)
        )

    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    assert len(prices) == periods

    data = pd.DataFrame(
        {
            "Open": prices,
            "High": [
                price + 0.02
                for price in prices
            ],
            "Low": [
                price - 0.02
                for price in prices
            ],
            "Close": prices,
            "Volume": [
                1_000_000
                for _ in range(periods)
            ],
        },
        index=dates,
    )

    return data


def test_strategy_engine():

    print(
        "\nCreating deterministic market data..."
    )

    data = make_market_data()

    print(
        f"Created {len(data)} candles"
    )

    # -----------------------------------------------------
    # Indicator calculation
    # -----------------------------------------------------

    data = IndicatorEngine.add_indicators(
        data
    )

    # -----------------------------------------------------
    # Strategy evaluation
    # -----------------------------------------------------

    engine = StrategyEngine()

    signal = engine.evaluate(
        "RR",
        data,
    )

    # -----------------------------------------------------
    # Display result
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("STRATEGY ENGINE RESULT")
    print("=" * 60)

    print(signal)

    # -----------------------------------------------------
    # Assertions
    # -----------------------------------------------------

    assert signal.symbol == "RR"

    assert signal.signal in (
        "BUY",
        "SELL",
        "HOLD",
    )

    assert signal.price > 0

    assert signal.stop_loss > 0

    assert signal.target > 0