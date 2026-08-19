from tradepilotai_os.strategy.supply_demand.models import (
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.orchestrator import (
    SupplyDemandOrchestrator,
)
from tradepilotai_os.strategy.supply_demand.orchestrator_models import (
    StrategyStage,
)
from tradepilotai_os.strategy.supply_demand.retest import (
    RetestCandle,
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
        retest_candle_count=0,
    )


def make_candle(
    timestamp,
    open_price,
    high,
    low,
    close,
):
    return RetestCandle(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        candle_number=0,
    )


# ============================================================
# ZONE CONNECTION
# ============================================================


def test_orchestrator_can_set_active_zone():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    assert orchestrator.state.active_zone is zone
    assert (
        orchestrator.state.stage
        == StrategyStage.ZONE_IDENTIFIED
    )


# ============================================================
# RETEST START
# ============================================================


def test_start_retest_uses_existing_retest_engine():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    result = orchestrator.start_retest(candle)

    assert result.candle_number == 1

    assert (
        result.timestamp
        == "2026-08-13 14:00"
    )

    assert orchestrator.state.retest_started is True

    assert (
        orchestrator.state.retest_candle_count
        == 1
    )

    assert (
        orchestrator.state.timestamp
        == "2026-08-13 14:00"
    )


def test_start_retest_changes_zone_to_retesting():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(candle)

    assert zone.status == ZoneStatus.RETESTING

    assert zone.retest_candle_count == 1


def test_retest_start_creates_candle_one():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    result = orchestrator.start_retest(candle)

    assert result.candle_number == 1
    assert result.open == candle.open
    assert result.high == candle.high
    assert result.low == candle.low
    assert result.close == candle.close


def test_retest_cannot_start_without_active_zone():
    orchestrator = SupplyDemandOrchestrator()

    candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    try:
        orchestrator.start_retest(candle)
    except ValueError as exc:
        assert "active zone" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_retest_engine_still_rejects_candle_outside_zone():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    candle = make_candle(
        "2026-08-13 14:00",
        1.27200,
        1.27210,
        1.27180,
        1.27205,
    )

    try:
        orchestrator.start_retest(candle)
    except ValueError as exc:
        assert "does not return into the zone" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


# ============================================================
# FOLLOWING RETEST CANDLES
# ============================================================


def test_second_retest_candle_is_numbered_two():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)

    second = make_candle(
        "2026-08-13 15:00",
        1.27102,
        1.27112,
        1.27085,
        1.27100,
    )

    result = orchestrator.process_retest_candle(
        second
    )

    assert result.candle_number == 2

    assert (
        orchestrator.state.retest_candle_count
        == 2
    )


def test_retest_candle_count_follows_retest_engine():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)

    for number in range(2, 7):
        candle = make_candle(
            f"2026-08-13 {number + 13:02d}:00",
            1.27100,
            1.27115,
            1.27080,
            1.27105,
        )

        result = orchestrator.process_retest_candle(
            candle
        )

        assert result.candle_number == number
        assert (
            orchestrator.state.retest_candle_count
            == number
        )


def test_processing_after_candle_four_is_allowed():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)

    for number in range(2, 7):
        candle = make_candle(
            f"2026-08-13 {number + 13:02d}:00",
            1.27100,
            1.27115,
            1.27080,
            1.27105,
        )

        result = orchestrator.process_retest_candle(
            candle
        )

        assert result.candle_number == number

    assert (
        orchestrator.state.retest_candle_count
        == 6
    )


# ============================================================
# FOUR-CANDLE OPPORTUNITY WINDOW
# ============================================================


def test_first_four_candles_are_inside_opportunity_window():
    orchestrator = SupplyDemandOrchestrator()

    assert (
        orchestrator.within_entry_opportunity_window(1)
        is True
    )

    assert (
        orchestrator.within_entry_opportunity_window(2)
        is True
    )

    assert (
        orchestrator.within_entry_opportunity_window(3)
        is True
    )

    assert (
        orchestrator.within_entry_opportunity_window(4)
        is True
    )


def test_fifth_candle_is_outside_opportunity_window():
    orchestrator = SupplyDemandOrchestrator()

    assert (
        orchestrator.within_entry_opportunity_window(5)
        is False
    )


def test_opportunity_window_does_not_stop_retest_processing():
    """
    This is important.

    Candle 5 is outside the normal four-candle entry
    opportunity window, but the retest engine must still
    process it because a multi-candle pattern may have
    started during candles 1-4 and need to complete later.
    """

    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)

    for number in range(2, 6):
        candle = make_candle(
            f"2026-08-13 {number + 13:02d}:00",
            1.27100,
            1.27115,
            1.27080,
            1.27105,
        )

        result = orchestrator.process_retest_candle(
            candle
        )

        assert result.candle_number == number

    assert (
        orchestrator.state.retest_candle_count
        == 5
    )

    assert (
        orchestrator.within_entry_opportunity_window(5)
        is False
    )

    assert (
        orchestrator.state.stage
        == StrategyStage.LOOKING_FOR_ENTRY
    )


# ============================================================
# STATE / RETEST SYNCHRONISATION
# ============================================================


def test_state_timestamp_follows_latest_retest_candle():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)

    second = make_candle(
        "2026-08-13 15:00",
        1.27102,
        1.27112,
        1.27085,
        1.27100,
    )

    orchestrator.process_retest_candle(second)

    assert (
        orchestrator.state.timestamp
        == "2026-08-13 15:00"
    )


def test_retest_processing_moves_state_to_looking_for_entry():
    orchestrator = SupplyDemandOrchestrator()
    zone = make_zone()

    orchestrator.set_active_zone(zone)

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)

    second = make_candle(
        "2026-08-13 15:00",
        1.27102,
        1.27112,
        1.27085,
        1.27100,
    )

    orchestrator.process_retest_candle(second)

    assert (
        orchestrator.state.stage
        == StrategyStage.LOOKING_FOR_ENTRY
    )