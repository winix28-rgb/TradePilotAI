import pandas as pd

from tradepilotai_os.strategy.supply_demand.models import (
    MarketStructure,
    SwingType,
)
from tradepilotai_os.strategy.supply_demand.structure import (
    H1StructureEngine,
)


def make_data(highs, lows):
    return pd.DataFrame(
        {
            "Open": lows,
            "High": highs,
            "Low": lows,
            "Close": highs,
        }
    )


def test_empty_data_is_unknown():
    engine = H1StructureEngine()

    result = engine.analyse(pd.DataFrame())

    assert result.direction == MarketStructure.UNKNOWN


def test_higher_high_and_higher_low_is_bullish():
    highs = [
        1.10,
        1.20,
        1.15,
        1.30,
        1.25,
        1.40,
        1.35,
    ]

    lows = [
        1.00,
        1.05,
        1.02,
        1.10,
        1.08,
        1.20,
        1.15,
    ]

    engine = H1StructureEngine()

    result = engine.analyse(
        make_data(highs, lows)
    )

    assert result.direction == MarketStructure.BULLISH
    assert len(result.higher_highs) >= 1
    assert len(result.higher_lows) >= 1


def test_lower_high_and_lower_low_is_bearish():
    highs = [
        1.40,
        1.30,
        1.35,
        1.20,
        1.25,
        1.10,
        1.15,
    ]

    lows = [
        1.30,
        1.20,
        1.25,
        1.10,
        1.15,
        1.00,
        1.05,
    ]

    engine = H1StructureEngine()

    result = engine.analyse(
        make_data(highs, lows)
    )

    assert result.direction == MarketStructure.BEARISH
    assert len(result.lower_highs) >= 1
    assert len(result.lower_lows) >= 1


def test_swing_types_are_recorded():
    highs = [
        1.10,
        1.20,
        1.15,
        1.30,
        1.25,
        1.35,
        1.30,
    ]

    lows = [
        1.00,
        1.05,
        1.02,
        1.10,
        1.08,
        1.15,
        1.12,
    ]

    engine = H1StructureEngine()

    result = engine.analyse(
        make_data(highs, lows)
    )

    swing_types = {
        swing.swing_type
        for swing in result.swing_points
    }

    assert SwingType.HIGHER_HIGH in swing_types
    assert SwingType.HIGHER_LOW in swing_types