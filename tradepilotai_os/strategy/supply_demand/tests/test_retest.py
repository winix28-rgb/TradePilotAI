import pytest

from tradepilotai_os.strategy.supply_demand.models import (
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.retest import (
    RetestCandle,
    SupplyDemandRetestEngine,
)


def make_zone():
    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27090,
        created_at="2026-08-13 10:00",
        breakout_time="2026-08-13 10:00",
        status=ZoneStatus.ACTIVE,
    )


def make_candle(
    timestamp,
    open_price,
    high,
    low,
    close,
    candle_number=0,
):
    return RetestCandle(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        candle_number=candle_number,
    )


def test_first_return_to_zone_starts_retest_at_candle_one():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    candle = make_candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27098,
        1.27105,
    )

    result = engine.start_retest(zone, candle)

    assert result.candle_number == 1
    assert zone.status == ZoneStatus.RETESTING
    assert zone.retest_candle_count == 1
    assert zone.retest_started_at == "2026-08-13 14:00"


def test_candle_above_zone_does_not_start_retest():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    candle = make_candle(
        "2026-08-13 14:00",
        1.27200,
        1.27220,
        1.27150,
        1.27180,
    )

    with pytest.raises(ValueError, match="does not return into the zone"):
        engine.start_retest(zone, candle)


def test_second_retest_candle_is_number_two():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    first = make_candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27098,
        1.27105,
    )

    second = make_candle(
        "2026-08-13 15:00",
        1.27105,
        1.27112,
        1.27092,
        1.27100,
    )

    engine.start_retest(zone, first)

    result = engine.process_retest_candle(
        zone,
        second,
    )

    assert result.candle_number == 2
    assert zone.retest_candle_count == 2


def test_fourth_candle_is_last_normal_entry_opportunity():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    first = make_candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27098,
        1.27105,
    )

    engine.start_retest(zone, first)

    for number in range(2, 5):
        candle = make_candle(
            f"2026-08-13 {14 + number}:00",
            1.27105,
            1.27112,
            1.27092,
            1.27100,
        )

        result = engine.process_retest_candle(
            zone,
            candle,
        )

        assert result.candle_number == number

    assert zone.retest_candle_count == 4

    assert engine.within_entry_opportunity_window(4) is True


def test_fifth_candle_can_complete_pattern_started_within_window():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    first = make_candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27098,
        1.27105,
    )

    engine.start_retest(zone, first)

    for number in range(2, 5):
        candle = make_candle(
            f"2026-08-13 {14 + number}:00",
            1.27105,
            1.27112,
            1.27092,
            1.27100,
        )

        engine.process_retest_candle(
            zone,
            candle,
        )

    fifth = make_candle(
        "2026-08-13 19:00",
        1.27100,
        1.27110,
        1.27090,
        1.27102,
    )

    result = engine.process_retest_candle(
        zone,
        fifth,
    )

    assert result.candle_number == 5
    assert zone.retest_candle_count == 5


def test_sixth_candle_can_complete_pattern_started_on_candle_four():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    first = make_candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27098,
        1.27105,
    )

    engine.start_retest(zone, first)

    for number in range(2, 7):
        candle = make_candle(
            f"2026-08-13 {14 + number}:00",
            1.27105,
            1.27112,
            1.27092,
            1.27100,
        )

        result = engine.process_retest_candle(
            zone,
            candle,
        )

    assert result.candle_number == 6
    assert zone.retest_candle_count == 6


def test_seventh_candle_can_be_trade_start_after_candle_six_entry():
    engine = SupplyDemandRetestEngine()
    zone = make_zone()

    first = make_candle(
        "2026-08-13 14:00",
        1.27120,
        1.27125,
        1.27098,
        1.27105,
    )

    engine.start_retest(zone, first)

    for number in range(2, 7):
        candle = make_candle(
            f"2026-08-13 {14 + number}:00",
            1.27105,
            1.27112,
            1.27092,
            1.27100,
        )

        engine.process_retest_candle(
            zone,
            candle,
        )

    seventh = make_candle(
        "2026-08-13 21:00",
        1.27108,
        1.27120,
        1.27100,
        1.27115,
    )

    result = engine.process_retest_candle(
        zone,
        seventh,
    )

    assert result.candle_number == 7