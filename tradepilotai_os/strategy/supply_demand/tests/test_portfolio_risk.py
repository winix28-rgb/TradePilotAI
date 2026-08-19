import pytest

from tradepilotai_os.risk.portfolio_risk import (
    PortfolioRiskController,
)


def test_one_percent_trade_is_permitted():
    controller = PortfolioRiskController(
        portfolio_value=100000.0,
        max_risk_percent=5.0,
        max_open_trades=5,
    )

    result = controller.assess(
        current_open_trades=0,
        current_risk_value=0.0,
        proposed_risk_value=1000.0,
    )

    assert result.permitted is True
    assert result.total_risk_value == pytest.approx(1000.0)
    assert result.total_risk_percent == pytest.approx(1.0)


def test_five_one_percent_trades_are_permitted():
    controller = PortfolioRiskController(
        portfolio_value=100000.0,
        max_risk_percent=5.0,
        max_open_trades=5,
    )

    result = controller.assess(
        current_open_trades=4,
        current_risk_value=4000.0,
        proposed_risk_value=1000.0,
    )

    assert result.permitted is True
    assert result.total_risk_value == pytest.approx(5000.0)
    assert result.total_risk_percent == pytest.approx(5.0)


def test_sixth_trade_is_rejected():
    controller = PortfolioRiskController(
        portfolio_value=100000.0,
        max_risk_percent=5.0,
        max_open_trades=5,
    )

    result = controller.assess(
        current_open_trades=5,
        current_risk_value=5000.0,
        proposed_risk_value=1000.0,
    )

    assert result.permitted is False
    assert "Maximum number of open trades" in result.reason


def test_risk_above_five_percent_is_rejected():
    controller = PortfolioRiskController(
        portfolio_value=100000.0,
        max_risk_percent=5.0,
        max_open_trades=5,
    )

    result = controller.assess(
        current_open_trades=4,
        current_risk_value=4000.0,
        proposed_risk_value=1500.0,
    )

    assert result.permitted is False
    assert "Maximum portfolio risk" in result.reason


def test_five_trades_with_less_than_five_percent_risk_are_allowed():
    controller = PortfolioRiskController(
        portfolio_value=100000.0,
        max_risk_percent=5.0,
        max_open_trades=5,
    )

    result = controller.assess(
        current_open_trades=4,
        current_risk_value=3200.0,
        proposed_risk_value=800.0,
    )

    assert result.permitted is True
    assert result.total_risk_value == pytest.approx(4000.0)
    assert result.total_risk_percent == pytest.approx(4.0)


def test_closed_trade_risk_can_be_replaced():
    controller = PortfolioRiskController(
        portfolio_value=100000.0,
        max_risk_percent=5.0,
        max_open_trades=4,
    )

    result = controller.assess(
        current_open_trades=3,
        current_risk_value=3000.0,
        proposed_risk_value=1000.0,
    )

    assert result.permitted is True
    assert result.total_risk_value == pytest.approx(4000.0)


def test_negative_current_trade_count_is_rejected():
    controller = PortfolioRiskController()

    with pytest.raises(ValueError):
        controller.assess(
            current_open_trades=-1,
            current_risk_value=0.0,
            proposed_risk_value=1000.0,
        )


def test_zero_proposed_risk_is_rejected():
    controller = PortfolioRiskController()

    with pytest.raises(ValueError):
        controller.assess(
            current_open_trades=0,
            current_risk_value=0.0,
            proposed_risk_value=0.0,
        )