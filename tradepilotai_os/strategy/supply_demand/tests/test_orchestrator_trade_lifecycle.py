"""
===========================================================
TradePilotAI OS
Supply & Demand Orchestrator Trade Lifecycle Tests
===========================================================

Step 2.5

These tests verify that the S&D orchestrator correctly
connects the existing TradeLifecycleEngine.

The existing lifecycle engine remains responsible for:

    - stop loss
    - take profit
    - exit reason
    - return calculation
    - WIN / LOSS

The orchestrator is responsible for transferring those
results into the S&D strategy state.
"""

import pytest

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

from tradepilotai_os.trading.trade_lifecycle import (
    TradeCandle,
    TradeLifecycle,
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
        entry_candle_time="2026-08-14 09:00",
        entry_candle_close=1.27110,
    )


def following_candle():
    return RetestCandle(
        timestamp="2026-08-14 10:00",
        open=1.27120,
        high=1.27130,
        low=1.27110,
        close=1.27125,
        candle_number=2,
    )


def prepare_orchestrator():
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

    orchestrator.calculate_trade_levels(
        risk_value=100.0
    )

    return orchestrator


def test_open_trade_requires_positive_risk_value():

    orchestrator = prepare_orchestrator()

    with pytest.raises(ValueError):
        orchestrator.open_trade(
            risk_value=0.0
        )


def test_open_trade_requires_trade_levels():

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

    with pytest.raises(ValueError):
        orchestrator.open_trade(
            risk_value=100.0
        )


def test_open_trade_creates_lifecycle_trade():

    orchestrator = prepare_orchestrator()

    trade = orchestrator.open_trade(
        risk_value=100.0
    )

    assert isinstance(
        trade,
        TradeLifecycle,
    )

    assert trade.status == "OPEN"

    assert trade.direction == "BUY"

    assert trade.entry_price == pytest.approx(
        1.27120
    )

    assert trade.stop_loss == pytest.approx(
        1.27040
    )

    assert trade.take_profit == pytest.approx(
        1.27280
    )

    assert trade.risk_value == pytest.approx(
        100.0
    )


def test_lifecycle_trade_is_stored_in_state():

    orchestrator = prepare_orchestrator()

    trade = orchestrator.open_trade(
        risk_value=100.0
    )

    assert (
        orchestrator.state.trade_lifecycle
        is trade
    )


def test_trade_remains_open_when_no_level_is_hit():

    orchestrator = prepare_orchestrator()

    trade = orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27120,
        high=1.27150,
        low=1.27080,
        close=1.27130,
    )

    result = orchestrator.process_trade_candle(
        candle
    )

    assert result.status == "OPEN"

    assert (
        orchestrator.state.trade_status
        == TradeStatus.OPEN
    )

    assert (
        orchestrator.state.stage
        == StrategyStage.TRADE_OPEN
    )

    assert (
        orchestrator.state.exit_time
        is None
    )


def test_buy_trade_closes_at_stop_loss():

    orchestrator = prepare_orchestrator()

    trade = orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27120,
        low=1.27030,
        close=1.27060,
    )

    result = orchestrator.process_trade_candle(
        candle
    )

    assert result is trade

    assert trade.status == "CLOSED"

    assert trade.exit_reason == "STOP_LOSS"

    assert trade.exit_price == pytest.approx(
        1.27040
    )

    assert trade.result == "LOSS"


def test_orchestrator_records_stop_loss():

    orchestrator = prepare_orchestrator()

    orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27120,
        low=1.27030,
        close=1.27060,
    )

    orchestrator.process_trade_candle(
        candle
    )

    assert (
        orchestrator.state.trade_status
        == TradeStatus.CLOSED
    )

    assert (
        orchestrator.state.stage
        == StrategyStage.TRADE_CLOSED
    )

    assert (
        orchestrator.state.exit_time
        == "2026-08-14 11:00"
    )

    assert (
        orchestrator.state.exit_price
        == pytest.approx(1.27040)
    )

    assert (
        orchestrator.state.exit_reason
        == "STOP_LOSS"
    )

    assert (
        orchestrator.state.trade_result
        == "LOSS"
    )


def test_buy_trade_closes_at_take_profit():

    orchestrator = prepare_orchestrator()

    trade = orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27290,
        low=1.27100,
        close=1.27250,
    )

    result = orchestrator.process_trade_candle(
        candle
    )

    assert result is trade

    assert trade.status == "CLOSED"

    assert trade.exit_reason == "TAKE_PROFIT"

    assert trade.exit_price == pytest.approx(
        1.27280
    )

    assert trade.result == "WIN"


def test_orchestrator_records_take_profit():

    orchestrator = prepare_orchestrator()

    orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27290,
        low=1.27100,
        close=1.27250,
    )

    orchestrator.process_trade_candle(
        candle
    )

    assert (
        orchestrator.state.trade_status
        == TradeStatus.CLOSED
    )

    assert (
        orchestrator.state.stage
        == StrategyStage.TRADE_CLOSED
    )

    assert (
        orchestrator.state.exit_reason
        == "TAKE_PROFIT"
    )

    assert (
        orchestrator.state.trade_result
        == "WIN"
    )

    assert (
        orchestrator.state.exit_price
        == pytest.approx(1.27280)
    )


def test_return_values_are_transferred_to_state():

    orchestrator = prepare_orchestrator()

    orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27290,
        low=1.27100,
        close=1.27250,
    )

    trade = orchestrator.process_trade_candle(
        candle
    )

    assert (
        orchestrator.state.return_value
        == pytest.approx(
            trade.return_value
        )
    )

    assert (
        orchestrator.state.return_percent
        == pytest.approx(
            trade.return_percent
        )
    )


def test_both_levels_hit_uses_stop_loss():

    orchestrator = prepare_orchestrator()

    orchestrator.open_trade(
        risk_value=100.0
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27120,
        high=1.27300,
        low=1.27020,
        close=1.27150,
    )

    trade = orchestrator.process_trade_candle(
        candle
    )

    assert trade.status == "CLOSED"

    assert trade.exit_reason == "STOP_LOSS"

    assert trade.exit_price == pytest.approx(
        1.27040
    )

    assert trade.result == "LOSS"