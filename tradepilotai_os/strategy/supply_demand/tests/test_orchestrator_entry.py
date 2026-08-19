from tradepilotai_os.strategy.supply_demand.entry_engine import (
    EntryDecision,
)
from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.orchestrator import (
    SupplyDemandOrchestrator,
)
from tradepilotai_os.strategy.supply_demand.orchestrator_models import (
    StrategyStage,
    TradeStatus,
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


def start_retest(
    orchestrator,
):
    orchestrator.set_active_zone(
        make_zone()
    )

    first = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.start_retest(first)


# ============================================================
# BASIC CONNECTION
# ============================================================


def test_orchestrator_contains_entry_engine():
    orchestrator = SupplyDemandOrchestrator()

    assert orchestrator.entry_engine is not None


def test_retest_candles_are_retained_for_entry_evaluation():
    orchestrator = SupplyDemandOrchestrator()

    start_retest(orchestrator)

    assert len(orchestrator.retest_candles) == 1
    assert (
        orchestrator.retest_candles[0].candle_number
        == 1
    )


def test_following_retest_candles_are_retained():
    orchestrator = SupplyDemandOrchestrator()

    start_retest(orchestrator)

    second = make_candle(
        "2026-08-13 15:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    third = make_candle(
        "2026-08-13 16:00",
        1.27100,
        1.27115,
        1.27080,
        1.27105,
    )

    orchestrator.process_retest_candle(second)
    orchestrator.process_retest_candle(third)

    assert len(orchestrator.retest_candles) == 3


# ============================================================
# PIN BAR
# ============================================================


def test_valid_pin_bar_is_passed_to_orchestrator_state():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        make_zone()
    )

    candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
    )

    orchestrator.start_retest(candle)

    decision = orchestrator.evaluate_entry(
        ZoneType.DEMAND
    )

    assert decision.valid is True
    assert decision.pattern == EntryPattern.PIN_BAR

    assert (
        decision.entry_candle_time
        == "2026-08-13 14:00"
    )

    assert (
        orchestrator.state.entry_candle_time
        == "2026-08-13 14:00"
    )

    assert (
        orchestrator.state.stage
        == StrategyStage.WAITING_FOR_TRADE_START
    )

    assert (
        orchestrator.state.trade_status
        == TradeStatus.WAITING
    )


# ============================================================
# THREE-CANDLE REVERSAL
# ============================================================


def test_three_candle_reversal_can_complete_on_candle_five():
    """
    The reversal begins on candle 3.

    Candle 3 = bearish
    Candle 4 = bullish
    Candle 5 = bullish completion

    Candle 5 is therefore the entry candle.
    """

    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        make_zone()
    )

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27110,
            1.27120,
            1.27100,
            1.27108,
        ),
        make_candle(
            "2026-08-13 15:00",
            1.27108,
            1.27115,
            1.27102,
            1.27106,
        ),
        make_candle(
            "2026-08-13 16:00",
            1.27120,
            1.27125,
            1.27095,
            1.27100,
        ),
        make_candle(
            "2026-08-13 17:00",
            1.27100,
            1.27110,
            1.27095,
            1.27105,
        ),
        make_candle(
            "2026-08-13 18:00",
            1.27105,
            1.27130,
            1.27100,
            1.27125,
        ),
    ]

    orchestrator.start_retest(
        candles[0]
    )

    for candle in candles[1:]:
        orchestrator.process_retest_candle(
            candle
        )

    decision = orchestrator.evaluate_entry(
        ZoneType.DEMAND
    )

    assert decision.valid is True

    assert (
        decision.pattern
        == EntryPattern.THREE_CANDLE_REVERSAL
    )

    assert (
        decision.entry_candle_time
        == "2026-08-13 18:00"
    )

    assert (
        orchestrator.state.entry_candle_time
        == "2026-08-13 18:00"
    )


def test_three_candle_reversal_can_begin_on_candle_four():
    """
    Candle 4 starts the pattern.

    Candle 5 continues it.

    Candle 6 completes it.

    Therefore candle 6 is the entry candle.
    """

    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        make_zone()
    )

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27105,
            1.27110,
            1.27100,
            1.27102,
        ),
        make_candle(
            "2026-08-13 15:00",
            1.27102,
            1.27108,
            1.27098,
            1.27104,
        ),
        make_candle(
            "2026-08-13 16:00",
            1.27104,
            1.27110,
            1.27098,
            1.27102,
        ),
        make_candle(
            "2026-08-13 17:00",
            1.27110,
            1.27115,
            1.27090,
            1.27100,
        ),
        make_candle(
            "2026-08-13 18:00",
            1.27100,
            1.27110,
            1.27095,
            1.27102,
        ),
        make_candle(
            "2026-08-13 19:00",
            1.27102,
            1.27130,
            1.27100,
            1.27120,
        ),
    ]

    orchestrator.start_retest(
        candles[0]
    )

    for candle in candles[1:]:
        orchestrator.process_retest_candle(
            candle
        )

    decision = orchestrator.evaluate_entry(
        ZoneType.DEMAND
    )

    assert decision.valid is True

    assert (
        decision.pattern
        == EntryPattern.THREE_CANDLE_REVERSAL
    )

    assert (
        decision.entry_candle_time
        == "2026-08-13 19:00"
    )


# ============================================================
# NO NEW PATTERN AFTER FOUR
# ============================================================


def test_pin_bar_on_candle_five_does_not_create_new_entry():
    """
    Candles 1-4 contain no valid pattern.

    Candle 5 is a valid Pin Bar.

    Because a Pin Bar is a one-candle pattern, it cannot
    START after the four-candle opportunity window.

    Therefore there is no entry.
    """

    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        make_zone()
    )

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27100,
            1.27110,
            1.27100,
            1.27108,
        ),
        make_candle(
            "2026-08-13 15:00",
            1.27108,
            1.27118,
            1.27108,
            1.27116,
        ),
        make_candle(
            "2026-08-13 16:00",
            1.27116,
            1.27126,
            1.27116,
            1.27124,
        ),
        make_candle(
            "2026-08-13 17:00",
            1.27124,
            1.27134,
            1.27124,
            1.27132,
        ),
        make_candle(
            "2026-08-13 18:00",
            1.27103,
            1.27110,
            1.27050,
            1.27108,
        ),
    ]

    orchestrator.start_retest(
        candles[0]
    )

    for candle in candles[1:]:
        orchestrator.process_retest_candle(
            candle
        )

    decision = orchestrator.evaluate_entry(
        ZoneType.DEMAND
    )

    assert decision.valid is False
    assert decision.pattern is None

    assert (
        orchestrator.state.entry_decision
        is None
    )


# ============================================================
# FIRST VALID PATTERN
# ============================================================


def test_first_valid_pattern_is_preserved():
    orchestrator = SupplyDemandOrchestrator()

    start_retest(orchestrator)

    decision = EntryDecision(
        valid=True,
        pattern=EntryPattern.PIN_BAR,
        entry_candle_time="2026-08-13 14:00",
        entry_candle_close=1.27110,
    )

    orchestrator.state.set_entry_decision(
        decision
    )

    result = orchestrator.evaluate_entry(
        ZoneType.DEMAND
    )

    assert result is decision

    assert (
        result.pattern
        == EntryPattern.PIN_BAR
    )