from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.zones import (
    SupplyDemandZoneEngine,
)


def test_create_demand_zone():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_demand_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27095,
        zone_top=1.27104,
        zone_bottom=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27140,
    )

    assert zone.zone_type == ZoneType.DEMAND
    assert zone.status == ZoneStatus.ACTIVE
    assert zone.top == 1.27104
    assert zone.bottom == 1.27095
    assert zone.structure_start_time == "2026-08-13 08:00"
    assert zone.breakout_time == "2026-08-13 10:00"
    assert zone.breakout_price == 1.27140


def test_create_supply_zone():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_supply_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27500,
        zone_top=1.27500,
        zone_bottom=1.27490,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27440,
    )

    assert zone.zone_type == ZoneType.SUPPLY
    assert zone.status == ZoneStatus.ACTIVE
    assert zone.top == 1.27500
    assert zone.bottom == 1.27490
    assert zone.structure_start_time == "2026-08-13 08:00"
    assert zone.breakout_time == "2026-08-13 10:00"


def test_zone_cannot_activate_before_breakout_closes():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_demand_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27095,
        zone_top=1.27104,
        zone_bottom=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27140,
    )

    try:
        engine.activate_zone(
            zone,
            breakout_candle_closed=False,
        )
    except ValueError as exc:
        assert "breakout candle has closed" in str(exc)
    else:
        raise AssertionError(
            "Zone should not activate before breakout close."
        )


def test_breakout_gap_is_not_mitigation():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_demand_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27095,
        zone_top=1.27104,
        zone_bottom=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27140,
    )

    # The breakout has closed above the zone.
    # That departure is not mitigation.
    zone = engine.activate_zone(
        zone,
        breakout_candle_closed=True,
    )

    assert zone.status == ZoneStatus.ACTIVE
    assert zone.mitigation_time is None
    assert zone.mitigation_reason is None


def test_retest_starts_at_one():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_demand_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27095,
        zone_top=1.27104,
        zone_bottom=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27140,
    )

    zone = engine.start_retest(
        zone,
        timestamp="2026-08-13 14:00",
    )

    assert zone.status == ZoneStatus.RETESTING
    assert zone.retest_candle_count == 1
    assert zone.retest_started_at == "2026-08-13 14:00"


def test_mitigation_changes_zone_status():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_supply_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27500,
        zone_top=1.27500,
        zone_bottom=1.27490,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27440,
    )

    zone = engine.mitigate_zone(
        zone,
        timestamp="2026-08-13 16:00",
        reason="CANDLE_CLOSED_BELOW_ZONE",
    )

    assert zone.status == ZoneStatus.MITIGATED
    assert zone.mitigation_time == "2026-08-13 16:00"
    assert zone.mitigation_reason == "CANDLE_CLOSED_BELOW_ZONE"


def test_trade_starts_on_next_candle():
    engine = SupplyDemandZoneEngine()

    zone = engine.create_demand_zone(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_price=1.27095,
        zone_top=1.27104,
        zone_bottom=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_price=1.27140,
    )

    zone = engine.mark_traded(
        zone=zone,
        entry_pattern=EntryPattern.PIN_BAR,
        entry_candle_time="2026-08-13 14:00",
        trade_start_time="2026-08-13 15:00",
        trade_start_price=1.27110,
    )

    assert zone.status == ZoneStatus.TRADED
    assert zone.entry_pattern == EntryPattern.PIN_BAR
    assert zone.entry_candle_time == "2026-08-13 14:00"
    assert zone.trade_start_time == "2026-08-13 15:00"
    assert zone.entry_time == "2026-08-13 15:00"
    assert zone.entry_price == 1.27110