import pytest

from tradepilotai_os.strategy.supply_demand.models import (
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.trade_levels import (
    SupplyDemandTradeLevelEngine,
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


def test_demand_stop_is_five_pips_below_zone():
    engine = SupplyDemandTradeLevelEngine()

    levels = engine.calculate(
        zone=demand_zone(),
        entry_price=1.27120,
        risk_value=100.0,
    )

    assert levels.direction == "BUY"
    assert levels.stop_loss == pytest.approx(1.27040)
    assert levels.risk_value == pytest.approx(100.0)


def test_supply_stop_is_five_pips_above_zone():
    engine = SupplyDemandTradeLevelEngine()

    levels = engine.calculate(
        zone=supply_zone(),
        entry_price=1.27470,
        risk_value=100.0,
    )

    assert levels.direction == "SELL"
    assert levels.stop_loss == pytest.approx(1.27560)
    assert levels.risk_value == pytest.approx(100.0)


def test_demand_take_profit_is_two_risk():
    engine = SupplyDemandTradeLevelEngine()

    levels = engine.calculate(
        zone=demand_zone(),
        entry_price=1.27120,
    )

    expected_risk = 1.27120 - 1.27040

    expected_tp = 1.27120 + (
        expected_risk * 2
    )

    assert levels.risk_distance == pytest.approx(
        expected_risk
    )

    assert levels.take_profit == pytest.approx(
        expected_tp
    )


def test_supply_take_profit_is_two_risk():
    engine = SupplyDemandTradeLevelEngine()

    levels = engine.calculate(
        zone=supply_zone(),
        entry_price=1.27470,
    )

    expected_risk = 1.27560 - 1.27470

    expected_tp = 1.27470 - (
        expected_risk * 2
    )

    assert levels.risk_distance == pytest.approx(
        expected_risk
    )

    assert levels.take_profit == pytest.approx(
        expected_tp
    )


def test_risk_distance_is_based_on_actual_entry():
    engine = SupplyDemandTradeLevelEngine()

    entry_price = 1.27120

    levels = engine.calculate(
        zone=demand_zone(),
        entry_price=entry_price,
    )

    expected_risk_distance = (
        entry_price - levels.stop_loss
    )

    assert levels.risk_distance == pytest.approx(
        expected_risk_distance
    )


def test_stop_buffer_is_five_pips():
    engine = SupplyDemandTradeLevelEngine()

    levels = engine.calculate(
        zone=demand_zone(),
        entry_price=1.27120,
    )

    assert levels.stop_pips == pytest.approx(8.0)


def test_invalid_entry_is_rejected():
    engine = SupplyDemandTradeLevelEngine()

    try:
        engine.calculate(
            zone=demand_zone(),
            entry_price=0.0,
        )
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError(
            "Invalid entry should be rejected."
        )