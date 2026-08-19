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

from tradepilotai_os.strategy.supply_demand.trade_levels import (
    TradeLevels,
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


def supply_zone():
    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.SUPPLY,
        top=1.27510,
        bottom=1.27490,
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


def test_trade_levels_require_active_zone():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.state.trade_start_price = 1.27120

    try:
        orchestrator.calculate_trade_levels()
    except ValueError as exc:
        assert "active zone" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_trade_levels_require_entry_decision():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.trade_start_price = 1.27120

    try:
        orchestrator.calculate_trade_levels()
    except ValueError as exc:
        assert "entry decision" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_trade_levels_require_actual_trade_entry_price():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    try:
        orchestrator.calculate_trade_levels()
    except ValueError as exc:
        assert "actual trade entry price" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_demand_trade_levels_use_actual_trade_entry():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.state.trade_start_price = 1.27120

    levels = orchestrator.calculate_trade_levels()

    assert isinstance(
        levels,
        TradeLevels,
    )

    assert levels.direction == "BUY"
    assert levels.entry_price == 1.27120
    assert levels.stop_loss == 1.27040
    assert levels.take_profit == 1.27280


def test_demand_levels_are_stored_in_state():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.state.trade_start_price = 1.27120

    levels = orchestrator.calculate_trade_levels()

    assert (
        orchestrator.state.trade_levels
        is levels
    )


def test_supply_trade_levels_use_actual_trade_entry():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        supply_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.state.trade_start_price = 1.27470

    levels = orchestrator.calculate_trade_levels()

    assert levels.direction == "SELL"
    assert levels.entry_price == 1.27470
    assert levels.stop_loss == 1.27560
    assert levels.take_profit == 1.27290


def test_risk_value_is_passed_to_trade_level_engine():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.state.trade_start_price = 1.27120

    levels = orchestrator.calculate_trade_levels(
        risk_value=100.0
    )

    assert levels.risk_value == 100.0


def test_risk_distance_is_based_on_actual_entry():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    orchestrator.state.set_entry_decision(
        valid_entry_decision()
    )

    orchestrator.state.trade_start_price = 1.27120

    levels = orchestrator.calculate_trade_levels()

    expected = round(
        1.27120 - levels.stop_loss,
        5,
    )

    assert levels.risk_distance == expected


def test_trade_levels_are_not_based_on_entry_candle_close():
    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        demand_zone()
    )

    decision = valid_entry_decision()

    orchestrator.state.set_entry_decision(
        decision
    )

    orchestrator.state.trade_start_price = 1.27120

    levels = orchestrator.calculate_trade_levels()

    assert levels.entry_price == 1.27120

    assert (
        levels.entry_price
        != decision.entry_candle_close
    )