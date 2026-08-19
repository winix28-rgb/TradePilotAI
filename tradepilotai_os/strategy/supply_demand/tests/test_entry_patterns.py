from tradepilotai_os.strategy.supply_demand.entry_patterns import (
    Candle,
    SupplyDemandEntryPatternEngine,
)
from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    ZoneType,
)


def candle(
    timestamp,
    open_price,
    high,
    low,
    close,
):
    return Candle(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
    )


def test_bullish_pin_bar():
    engine = SupplyDemandEntryPatternEngine()

    pin = candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
    )

    assert engine.identify_pin_bar(
        pin,
        ZoneType.DEMAND,
    ) is True


def test_bearish_pin_bar():
    engine = SupplyDemandEntryPatternEngine()

    pin = candle(
        "2026-08-13 14:00",
        1.27110,
        1.27160,
        1.27100,
        1.27105,
    )

    assert engine.identify_pin_bar(
        pin,
        ZoneType.SUPPLY,
    ) is True


def test_large_body_is_not_pin_bar():
    engine = SupplyDemandEntryPatternEngine()

    candle_with_large_body = candle(
        "2026-08-13 14:00",
        1.27000,
        1.27110,
        1.26990,
        1.27100,
    )

    assert engine.identify_pin_bar(
        candle_with_large_body,
        ZoneType.DEMAND,
    ) is False


def test_bullish_engulfing():
    engine = SupplyDemandEntryPatternEngine()

    previous = candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27090,
        1.27100,
    )

    current = candle(
        "2026-08-13 15:00",
        1.27095,
        1.27140,
        1.27085,
        1.27130,
    )

    assert engine.identify_engulfing(
        previous,
        current,
        ZoneType.DEMAND,
    ) is True


def test_bearish_engulfing():
    engine = SupplyDemandEntryPatternEngine()

    previous = candle(
        "2026-08-13 14:00",
        1.27100,
        1.27130,
        1.27090,
        1.27120,
    )

    current = candle(
        "2026-08-13 15:00",
        1.27125,
        1.27135,
        1.27070,
        1.27080,
    )

    assert engine.identify_engulfing(
        previous,
        current,
        ZoneType.SUPPLY,
    ) is True


def test_bullish_three_candle_reversal():
    engine = SupplyDemandEntryPatternEngine()

    first = candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27090,
        1.27100,
    )

    second = candle(
        "2026-08-13 15:00",
        1.27100,
        1.27115,
        1.27095,
        1.27105,
    )

    third = candle(
        "2026-08-13 16:00",
        1.27105,
        1.27145,
        1.27100,
        1.27130,
    )

    assert engine.identify_three_candle_reversal(
        first,
        second,
        third,
        ZoneType.DEMAND,
    ) is True


def test_bearish_three_candle_reversal():
    engine = SupplyDemandEntryPatternEngine()

    first = candle(
        "2026-08-13 14:00",
        1.27090,
        1.27130,
        1.27085,
        1.27120,
    )

    second = candle(
        "2026-08-13 15:00",
        1.27120,
        1.27125,
        1.27100,
        1.27105,
    )

    third = candle(
        "2026-08-13 16:00",
        1.27105,
        1.27110,
        1.27060,
        1.27075,
    )

    assert engine.identify_three_candle_reversal(
        first,
        second,
        third,
        ZoneType.SUPPLY,
    ) is True


def test_first_valid_pin_bar_is_returned():
    engine = SupplyDemandEntryPatternEngine()

    pin = candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
    )

    result = engine.identify_first_valid_pattern(
        [pin],
        ZoneType.DEMAND,
    )

    assert result == EntryPattern.PIN_BAR


def test_no_pattern_returns_none():
    engine = SupplyDemandEntryPatternEngine()

    ordinary = candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27095,
        1.27105,
    )

    result = engine.identify_first_valid_pattern(
        [ordinary],
        ZoneType.DEMAND,
    )

    assert result is None