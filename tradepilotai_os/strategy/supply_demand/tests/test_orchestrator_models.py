from tradepilotai_os.strategy.supply_demand.entry_engine import (
    EntryDecision,
)
from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.orchestrator_models import (
    StrategyStage,
    SupplyDemandOrchestratorState,
    TradeStatus,
)


def make_zone():
    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27090,
        created_at="2026-08-13 10:00",
        breakout_time="2026-08-13 10:00",
        status=ZoneStatus.RETESTING,
        retest_candle_count=1,
    )


def make_entry_decision():
    return EntryDecision(
        valid=True,
        pattern=EntryPattern.PIN_BAR,
        entry_candle_time="2026-08-13 14:00",
        entry_candle_close=1.27110,
    )


def test_new_state_starts_idle():
    state = SupplyDemandOrchestratorState()

    assert state.stage == StrategyStage.IDLE
    assert state.trade_status == TradeStatus.NOT_STARTED

    assert state.active_zone is None
    assert state.entry_decision is None

    assert state.entry_candle_time is None
    assert state.entry_candle_close is None

    assert state.trade_start_time is None
    assert state.trade_start_price is None


def test_zone_can_be_set():
    state = SupplyDemandOrchestratorState()
    zone = make_zone()

    state.set_zone(zone)

    assert state.active_zone is zone
    assert state.stage == StrategyStage.ZONE_IDENTIFIED

    assert (
        state.stage_history[-1]
        == StrategyStage.ZONE_IDENTIFIED
    )


def test_retest_can_be_started():
    state = SupplyDemandOrchestratorState()

    state.set_zone(make_zone())
    state.start_retest()

    assert state.retest_started is True
    assert state.retest_candle_count == 0
    assert state.stage == StrategyStage.RETESTING


def test_retest_candles_are_counted():
    state = SupplyDemandOrchestratorState()

    state.set_zone(make_zone())
    state.start_retest()

    state.add_retest_candle()
    state.add_retest_candle()
    state.add_retest_candle()

    assert state.retest_candle_count == 3
    assert state.stage == StrategyStage.LOOKING_FOR_ENTRY


def test_cannot_add_retest_candle_before_retest():
    state = SupplyDemandOrchestratorState()

    try:
        state.add_retest_candle()
    except ValueError as exc:
        assert "retest has started" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_valid_entry_decision_is_recorded():
    state = SupplyDemandOrchestratorState()

    decision = make_entry_decision()

    state.set_entry_decision(decision)

    assert state.entry_decision is decision

    assert (
        state.entry_candle_time
        == "2026-08-13 14:00"
    )

    assert state.entry_candle_close == 1.27110

    assert (
        state.stage
        == StrategyStage.WAITING_FOR_TRADE_START
    )

    assert (
        state.trade_status
        == TradeStatus.WAITING
    )


def test_invalid_entry_decision_is_rejected():
    state = SupplyDemandOrchestratorState()

    decision = EntryDecision(
        valid=False,
        pattern=None,
    )

    try:
        state.set_entry_decision(decision)
    except ValueError as exc:
        assert "invalid entry decision" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_trade_start_is_separate_from_entry_candle():
    state = SupplyDemandOrchestratorState()

    state.set_entry_decision(
        make_entry_decision()
    )

    state.start_trade(
        trade_start_time="2026-08-13 15:00",
        trade_start_price=1.27108,
    )

    assert (
        state.entry_candle_time
        == "2026-08-13 14:00"
    )

    assert (
        state.trade_start_time
        == "2026-08-13 15:00"
    )

    assert state.trade_start_price == 1.27108

    assert (
        state.entry_candle_time
        != state.trade_start_time
    )

    assert (
        state.stage
        == StrategyStage.TRADE_OPEN
    )

    assert (
        state.trade_status
        == TradeStatus.OPEN
    )


def test_trade_cannot_start_on_entry_candle():
    state = SupplyDemandOrchestratorState()

    state.set_entry_decision(
        make_entry_decision()
    )

    try:
        state.start_trade(
            trade_start_time="2026-08-13 14:00",
            trade_start_price=1.27110,
        )
    except ValueError as exc:
        assert (
            "different from the entry candle"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_trade_can_be_closed():
    state = SupplyDemandOrchestratorState()

    state.set_entry_decision(
        make_entry_decision()
    )

    state.start_trade(
        trade_start_time="2026-08-13 15:00",
        trade_start_price=1.27108,
    )

    state.close_trade(
        exit_time="2026-08-13 18:00",
        exit_price=1.27280,
        trade_result=172.0,
    )

    assert state.trade_status == TradeStatus.CLOSED

    assert (
        state.stage
        == StrategyStage.TRADE_CLOSED
    )

    assert state.exit_time == "2026-08-13 18:00"
    assert state.exit_price == 1.27280
    assert state.trade_result == 172.0


def test_trade_cannot_be_closed_before_it_is_open():
    state = SupplyDemandOrchestratorState()

    try:
        state.close_trade(
            exit_time="2026-08-13 18:00",
            exit_price=1.27280,
            trade_result=172.0,
        )
    except ValueError as exc:
        assert "not open" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_stage_history_records_progression():
    state = SupplyDemandOrchestratorState()

    state.set_zone(make_zone())
    state.start_retest()

    state.add_retest_candle()
    state.set_entry_decision(
        make_entry_decision()
    )

    state.start_trade(
        trade_start_time="2026-08-13 15:00",
        trade_start_price=1.27108,
    )

    assert state.stage_history == [
        StrategyStage.ZONE_IDENTIFIED,
        StrategyStage.RETESTING,
        StrategyStage.LOOKING_FOR_ENTRY,
        StrategyStage.ENTRY_IDENTIFIED,
        StrategyStage.WAITING_FOR_TRADE_START,
        StrategyStage.TRADE_OPEN,
    ]


def test_trade_start_price_is_actual_following_candle_open():
    state = SupplyDemandOrchestratorState()

    state.set_entry_decision(
        make_entry_decision()
    )

    state.start_trade(
        trade_start_time="2026-08-13 15:00",
        trade_start_price=1.27108,
    )

    assert state.trade_start_price == 1.27108

    assert (
        state.trade_start_price
        != state.entry_candle_close
    )