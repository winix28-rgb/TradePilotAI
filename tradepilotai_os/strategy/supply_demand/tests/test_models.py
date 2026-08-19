from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    H1Structure,
    MarketStructure,
    SupplyDemandZone,
    SwingPoint,
    SwingType,
    TimeframeTrend,
    TrendAlignment,
    TrendDirection,
    ZoneStatus,
    ZoneType,
)


def test_timeframe_trend():
    trend = TimeframeTrend(
        timeframe="Daily",
        direction=TrendDirection.BULLISH,
        ma50=100.0,
        ma200=95.0,
        price=105.0,
        candles_with_trend=True,
    )

    assert trend.timeframe == "Daily"
    assert trend.direction == TrendDirection.BULLISH
    assert trend.candles_with_trend is True


def test_h1_structure():
    swing = SwingPoint(
        timestamp="2026-08-12 10:00",
        price=1.2500,
        swing_type=SwingType.HIGHER_HIGH,
    )

    structure = H1Structure(
        direction=MarketStructure.BULLISH,
        latest_swing=swing,
        swing_points=[swing],
        higher_highs=[swing],
    )

    assert structure.direction == MarketStructure.BULLISH
    assert structure.latest_swing == swing
    assert len(structure.higher_highs) == 1


def test_demand_zone_contains_price():
    zone = SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.2500,
        bottom=1.2450,
        created_at="2026-08-12 10:00",
        breakout_time="2026-08-12 10:00",
    )

    assert zone.contains_price(1.2475)
    assert zone.contains_price(1.2450)
    assert zone.contains_price(1.2500)
    assert not zone.contains_price(1.2550)


def test_active_zone():
    zone = SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.2500,
        bottom=1.2450,
        created_at="2026-08-12 10:00",
        breakout_time="2026-08-12 10:00",
    )

    assert zone.status == ZoneStatus.ACTIVE
    assert zone.is_active is True


def test_mitigated_zone_is_not_active():
    zone = SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.2500,
        bottom=1.2450,
        created_at="2026-08-12 10:00",
        breakout_time="2026-08-12 10:00",
        status=ZoneStatus.MITIGATED,
    )

    assert zone.is_active is False


def test_trade_context_enums():
    assert EntryPattern.PIN_BAR.value == "PIN_BAR"
    assert EntryPattern.ENGULFING.value == "ENGULFING"
    assert EntryPattern.THREE_CANDLE_REVERSAL.value == "THREE_CANDLE_REVERSAL"

    assert TrendAlignment.WITH_TREND.value == "WITH_TREND"
    assert TrendAlignment.AGAINST_TREND.value == "AGAINST_TREND"