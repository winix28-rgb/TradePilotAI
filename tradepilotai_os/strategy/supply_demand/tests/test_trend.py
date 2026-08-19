import pandas as pd

from tradepilotai_os.strategy.supply_demand.models import TrendDirection
from tradepilotai_os.strategy.supply_demand.trend import (
    SupplyDemandTrendEngine,
)


def make_data(values):
    return pd.DataFrame(
        {
            "Open": values,
            "High": [value + 1 for value in values],
            "Low": [value - 1 for value in values],
            "Close": values,
        }
    )


def test_insufficient_data_is_neutral():
    values = list(range(1, 100))

    engine = SupplyDemandTrendEngine()

    result = engine.analyse_daily(
        make_data(values)
    )

    assert result.direction == TrendDirection.NEUTRAL
    assert result.ma50 is not None
    assert result.ma200 is None


def test_bullish_price_above_both_mas():
    values = list(range(1, 301))

    engine = SupplyDemandTrendEngine()

    result = engine.analyse_daily(
        make_data(values)
    )

    assert result.direction == TrendDirection.BULLISH
    assert result.ma50 is not None
    assert result.ma200 is not None
    assert result.price > result.ma50
    assert result.price > result.ma200


def test_bearish_price_below_both_mas():
    values = list(range(300, 0, -1))

    engine = SupplyDemandTrendEngine()

    result = engine.analyse_daily(
        make_data(values)
    )

    assert result.direction == TrendDirection.BEARISH
    assert result.ma50 is not None
    assert result.ma200 is not None
    assert result.price < result.ma50
    assert result.price < result.ma200


def test_h4_analysis_uses_h4_label():
    values = list(range(1, 301))

    engine = SupplyDemandTrendEngine()

    result = engine.analyse_h4(
        make_data(values)
    )

    assert result.timeframe == "H4"
    assert result.direction == TrendDirection.BULLISH