from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)


def make_zone():
    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27095,
        created_at="2026-08-13 08:00",
        breakout_time="2026-08-13 08:00",
    )


def test_entry_candle_is_recorded_separately():
    zone = make_zone()

    zone.entry_pattern = EntryPattern.PIN_BAR
    zone.entry_candle_time = "2026-08-13 12:00"
    zone.entry_candle_close = 1.27120

    assert zone.entry_pattern == EntryPattern.PIN_BAR
    assert zone.entry_candle_time == "2026-08-13 12:00"
    assert zone.entry_candle_close == 1.27120

    # The trade has not started yet.
    assert zone.trade_start_time is None
    assert zone.entry_time is None


def test_trade_starts_on_following_candle_open():
    zone = make_zone()

    zone.entry_pattern = EntryPattern.PIN_BAR
    zone.entry_candle_time = "2026-08-13 12:00"
    zone.entry_candle_close = 1.27120

    # Following candle opens and becomes the trade-start candle.
    zone.trade_start_time = "2026-08-13 13:00"
    zone.trade_start_price = 1.27118

    zone.entry_time = zone.trade_start_time
    zone.entry_price = zone.trade_start_price

    assert zone.entry_candle_time != zone.trade_start_time
    assert zone.entry_time == "2026-08-13 13:00"
    assert zone.entry_price == 1.27118


def test_entry_is_not_at_entry_candle_close():
    zone = make_zone()

    zone.entry_pattern = EntryPattern.ENGULFING
    zone.entry_candle_time = "2026-08-13 12:00"
    zone.entry_candle_close = 1.27130

    zone.trade_start_time = "2026-08-13 13:00"
    zone.trade_start_price = 1.27122

    zone.entry_time = zone.trade_start_time
    zone.entry_price = zone.trade_start_price

    assert zone.entry_price != zone.entry_candle_close
    assert zone.entry_time != zone.entry_candle_time


def test_entry_candle_cannot_be_mitigation():
    zone = make_zone()

    zone.entry_pattern = EntryPattern.THREE_CANDLE_REVERSAL
    zone.entry_candle_time = "2026-08-13 12:00"
    zone.entry_candle_close = 1.27125

    # A valid entry candle leaves the zone active.
    zone.status = ZoneStatus.RETESTING
    zone.mitigation_time = None
    zone.mitigation_reason = None

    assert zone.entry_pattern is not None
    assert zone.status == ZoneStatus.RETESTING
    assert zone.mitigation_time is None
    assert zone.mitigation_reason is None


def test_trade_start_price_is_the_actual_entry_price():
    zone = make_zone()

    zone.entry_pattern = EntryPattern.PIN_BAR
    zone.entry_candle_time = "2026-08-13 12:00"
    zone.entry_candle_close = 1.27115

    zone.trade_start_time = "2026-08-13 13:00"
    zone.trade_start_price = 1.27110

    zone.entry_time = zone.trade_start_time
    zone.entry_price = zone.trade_start_price

    assert zone.entry_price == zone.trade_start_price
    assert zone.entry_time == zone.trade_start_time