"""
===========================================================
TradePilotAI OS
Step 4 - S&D Portfolio Risk Orchestration Tests
===========================================================

Tests the connection between the existing S&D orchestrator
and the existing PortfolioRiskController.

AGREED PORTFOLIO RULES

    Maximum open trades = 5
    Maximum total portfolio risk = 5%

No additional risk rules are introduced by these tests.
"""

from __future__ import annotations

import pytest

from tradepilotai_os.risk.portfolio_risk import (
    PortfolioRiskController,
)

from tradepilotai_os.strategy.supply_demand.models import (
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)

from tradepilotai_os.strategy.supply_demand.orchestrator import (
    SupplyDemandOrchestrator,
)

from tradepilotai_os.strategy.supply_demand.orchestrator_models import (
    TradeStatus,
)


def make_demand_zone() -> SupplyDemandZone:
    """Create an active demand zone for the tests."""

    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27090,
        created_at="2026-08-14 08:00",
        breakout_time="2026-08-14 08:00",
        status=ZoneStatus.ACTIVE,
    )


def prepare_orchestrator() -> SupplyDemandOrchestrator:
    """
    Prepare an orchestrator for Step 4 testing.

    The S&D specialist engines are already tested separately.

    These tests specifically test the portfolio-risk gate.
    """

    orchestrator = SupplyDemandOrchestrator()

    orchestrator.set_active_zone(
        make_demand_zone()
    )

    # ---------------------------------------------------------
    # Move the state to the point immediately before the
    # portfolio-risk gate.
    #
    # This deliberately avoids rebuilding the complete S&D
    # candle sequence because that is already covered by the
    # existing Step 1-3 tests.
    # ---------------------------------------------------------

    orchestrator.state.trade_start_time = (
        "2026-08-14 14:00"
    )

    orchestrator.state.trade_start_price = (
        1.27120
    )

    orchestrator.state.trade_status = (
        TradeStatus.OPEN
    )

    # The orchestrator only needs trade_levels to exist in
    # order to reach the portfolio-risk assessment.
    orchestrator.state.trade_levels = object()

    return orchestrator


def test_step_4_default_rules_are_five_trades_and_five_percent():
    """
    Verify the agreed portfolio rules.
    """

    controller = PortfolioRiskController()

    assert controller.max_open_trades == 5

    assert controller.max_risk_percent == 5.0

    assert controller.max_risk_value == pytest.approx(
        5000.0
    )


def test_step_4_trade_is_permitted_within_both_limits():
    """
    A proposed trade is permitted when both portfolio limits
    remain within the agreed rules.
    """

    controller = PortfolioRiskController(
        portfolio_value=100000.0,
    )

    assessment = controller.assess(
        current_open_trades=2,
        current_risk_value=2000.0,
        proposed_risk_value=1000.0,
    )

    assert assessment.permitted is True

    assert assessment.current_open_trades == 2

    assert assessment.proposed_risk_value == pytest.approx(
        1000.0
    )

    assert assessment.total_risk_value == pytest.approx(
        3000.0
    )

    assert assessment.total_risk_percent == pytest.approx(
        3.0
    )


def test_step_4_fifth_open_trade_is_permitted():
    """
    The fifth open trade is allowed.

    The sixth trade would exceed the agreed maximum of five.
    """

    controller = PortfolioRiskController(
        portfolio_value=100000.0,
    )

    assessment = controller.assess(
        current_open_trades=4,
        current_risk_value=3000.0,
        proposed_risk_value=1000.0,
    )

    assert assessment.permitted is True

    assert assessment.current_open_trades == 4

    assert assessment.total_risk_value == pytest.approx(
        4000.0
    )


def test_step_4_sixth_open_trade_is_rejected():
    """
    A sixth open trade is rejected.
    """

    controller = PortfolioRiskController(
        portfolio_value=100000.0,
    )

    assessment = controller.assess(
        current_open_trades=5,
        current_risk_value=4000.0,
        proposed_risk_value=500.0,
    )

    assert assessment.permitted is False

    assert (
        "Maximum number of open trades"
        in assessment.reason
    )


def test_step_4_total_portfolio_risk_above_five_percent_is_rejected():
    """
    Total portfolio risk may not exceed 5%.
    """

    controller = PortfolioRiskController(
        portfolio_value=100000.0,
    )

    assessment = controller.assess(
        current_open_trades=2,
        current_risk_value=4500.0,
        proposed_risk_value=600.0,
    )

    assert assessment.permitted is False

    assert (
        "Maximum portfolio risk"
        in assessment.reason
    )

    assert assessment.total_risk_value == pytest.approx(
        5100.0
    )

    assert assessment.total_risk_percent == pytest.approx(
        5.1
    )


def test_step_4_exactly_five_percent_is_permitted():
    """
    Exactly 5% total portfolio risk is permitted.

    5% is the maximum, so exactly 5% remains valid.
    """

    controller = PortfolioRiskController(
        portfolio_value=100000.0,
    )

    assessment = controller.assess(
        current_open_trades=3,
        current_risk_value=4000.0,
        proposed_risk_value=1000.0,
    )

    assert assessment.permitted is True

    assert assessment.total_risk_value == pytest.approx(
        5000.0
    )

    assert assessment.total_risk_percent == pytest.approx(
        5.0
    )


def test_step_4_orchestrator_uses_portfolio_risk_controller():
    """
    Verify that the orchestrator uses the existing
    PortfolioRiskController.
    """

    orchestrator = prepare_orchestrator()

    assert isinstance(
        orchestrator.portfolio_risk_controller,
        PortfolioRiskController,
    )


def test_step_4_orchestrator_assesses_proposed_trade():
    """
    The orchestrator delegates the assessment to the existing
    PortfolioRiskController.
    """

    orchestrator = prepare_orchestrator()

    assessment = (
        orchestrator.assess_portfolio_risk(
            proposed_risk_value=1000.0,
            current_open_trades=2,
            current_risk_value=2000.0,
        )
    )

    assert assessment.permitted is True

    assert assessment.total_risk_value == pytest.approx(
        3000.0
    )

    assert assessment.total_risk_percent == pytest.approx(
        3.0
    )


def test_step_4_orchestrator_rejects_over_five_open_trades():
    """
    The orchestrator rejects a proposed sixth trade.

    The test first places the orchestrator at the point where
    the risk gate is reached.
    """

    orchestrator = prepare_orchestrator()

    with pytest.raises(
        ValueError,
        match="Maximum number of open trades",
    ):
        orchestrator.open_trade(
            risk_value=500.0,
            current_open_trades=5,
            current_risk_value=4000.0,
        )

    assert (
        orchestrator.last_risk_assessment is not None
    )

    assert (
        orchestrator.last_risk_assessment.permitted
        is False
    )


def test_step_4_orchestrator_rejects_over_five_percent_risk():
    """
    The orchestrator rejects a proposed trade that would
    take total portfolio risk above 5%.
    """

    orchestrator = prepare_orchestrator()

    with pytest.raises(
        ValueError,
        match="Maximum portfolio risk",
    ):
        orchestrator.open_trade(
            risk_value=600.0,
            current_open_trades=2,
            current_risk_value=4500.0,
        )

    assert (
        orchestrator.last_risk_assessment is not None
    )

    assert (
        orchestrator.last_risk_assessment.permitted
        is False
    )


def test_step_4_risk_assessment_is_stored():
    """
    The most recent portfolio-risk assessment is retained
    by the orchestrator.
    """

    orchestrator = prepare_orchestrator()

    assessment = (
        orchestrator.assess_portfolio_risk(
            proposed_risk_value=1000.0,
            current_open_trades=2,
            current_risk_value=2000.0,
        )
    )

    assert (
        orchestrator.last_risk_assessment
        is assessment
    )


def test_step_4_invalid_proposed_risk_is_rejected():
    """
    Existing PortfolioRiskController validation remains
    authoritative.
    """

    orchestrator = prepare_orchestrator()

    with pytest.raises(
        ValueError,
        match="Proposed risk value",
    ):
        orchestrator.assess_portfolio_risk(
            proposed_risk_value=0.0,
            current_open_trades=0,
            current_risk_value=0.0,
        )


def test_step_4_negative_current_risk_is_rejected():
    """
    Existing PortfolioRiskController validation remains
    authoritative.
    """

    orchestrator = prepare_orchestrator()

    with pytest.raises(
        ValueError,
        match="Current risk value",
    ):
        orchestrator.assess_portfolio_risk(
            proposed_risk_value=1000.0,
            current_open_trades=0,
            current_risk_value=-1.0,
        )


def test_step_4_negative_open_trade_count_is_rejected():
    """
    Existing PortfolioRiskController validation remains
    authoritative.
    """

    orchestrator = prepare_orchestrator()

    with pytest.raises(
        ValueError,
        match="Current open trades",
    ):
        orchestrator.assess_portfolio_risk(
            proposed_risk_value=1000.0,
            current_open_trades=-1,
            current_risk_value=0.0,
        )
