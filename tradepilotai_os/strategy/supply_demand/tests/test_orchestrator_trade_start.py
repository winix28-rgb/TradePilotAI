"""
===========================================================
TradePilotAI OS
Supply & Demand Orchestrator Trade Start Tests
===========================================================

Step 2.4

These tests verify that the orchestrator correctly connects
the completed entry candle to the actual trade start.

Rules:

    Entry pattern completes
        ↓
    Entry candle
        ↓
    Following candle
        ↓
    Following candle OPEN
        ↓
    Actual trade start

The entry candle close must never be used as the actual
trade entry price.
"""

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


def demand_zone():
    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27090,
        created_at="2026-08-13 10:00",
        breakout_time="2026-08-13 10:00",
        status=ZoneStatus.TRADED,
    )


def valid_entry_decision():
    return EntryDecision(
        valid=True,
        pattern=EntryPattern.PIN_BAR,
        entry_candle_time="2026-08-13 14:00",
        entry_candle_close=1.27110,
    )


def following_candle():
    return RetestCandle(
        timestamp="2026-08-13 15:00",
        open=1.27120,
        high=1.27130,
        low=1.27110,
        close=1.27125,
        candle_number=2,
    )


def test_trade_start_requires_active_zone():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    try:
        orchestrator.start_trade(
            following_candle()
        )
    except ValueError as exc:
        assert "active zone" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_trade_start_requires_entry_decision():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    try:
        orchestrator.start_trade(
            following_candle()
        )
    except ValueError as exc:
        assert "entry decision" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_trade_start_uses_following_candle_open():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    decision = orchestrator.start_trade(
        following_candle()
    )

    assert decision.trade_start_time == (
        "2026-08-13 15:00"
    )

    assert decision.trade_start_price == 1.27120


def test_trade_start_does_not_use_entry_candle_close():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    decision = valid_entry_decision()

    orchestrator.state.set_entry_decision(
        decision
    )

    result = orchestrator.start_trade(
        following_candle()
    )

    assert result.trade_start_price == 1.27120

    assert result.trade_start_price != (
        decision.entry_candle_close
    )


def test_trade_start_time_is_stored_in_state():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.start_trade(
        following_candle()
    )

    assert orchestrator.state.trade_start_time == (
        "2026-08-13 15:00"
    )


def test_trade_start_price_is_stored_in_state():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.start_trade(
        following_candle()
    )

    assert orchestrator.state.trade_start_price == (
        1.27120
    )


def test_trade_status_becomes_open():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.start_trade(
        following_candle()
    )

    assert (
        orchestrator.state.trade_status
        == TradeStatus.OPEN
    )


def test_strategy_stage_becomes_trade_open():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.start_trade(
        following_candle()
    )

    assert (
        orchestrator.state.stage
        == StrategyStage.TRADE_OPEN
    )


def test_trade_start_cannot_be_same_as_entry_candle():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    same_candle = RetestCandle(
        timestamp="2026-08-13 14:00",
        open=1.27110,
        high=1.27120,
        low=1.27100,
        close=1.27115,
        candle_number=1,
    )

    try:
        orchestrator.start_trade(
            same_candle
        )
    except ValueError as exc:
        assert "different" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_zone_receives_trade_start_details():
    orchestrator = SupplyDemandOrchestrator()

    zone = demand_zone()

    orchestrator.set_active_zone(
        zone
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.start_trade(
        following_candle()
    )

    assert zone.trade_start_time == (
        "2026-08-13 15:00"
    )

    assert zone.trade_start_price == 1.27120

    assert zone.entry_time == (
        "2026-08-13 15:00"
    )

    assert zone.entry_price == 1.27120