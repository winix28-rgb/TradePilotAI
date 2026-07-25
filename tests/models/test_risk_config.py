"""
===========================================================
TradePilotAI
Risk Configuration Tests
===========================================================
"""

import pytest

from models.risk_config import RiskConfig


def test_default_values():

    config = RiskConfig()

    assert config.risk_per_trade == 1.0
    assert config.max_positions == 10
    assert config.allow_short_positions is False
    assert config.commission == 0.0
    assert config.slippage == 0.0


def test_override_values():

    config = RiskConfig(
        risk_per_trade=2.0,
        max_positions=5,
        allow_short_positions=True,
        commission=5.00,
        slippage=0.10,
    )

    assert config.risk_per_trade == 2.0
    assert config.max_positions == 5
    assert config.allow_short_positions is True
    assert config.commission == 5.00
    assert config.slippage == 0.10


def test_config_is_immutable():

    config = RiskConfig()

    with pytest.raises(Exception):
        config.max_positions = 20


# =========================================================
# Validation Tests
# =========================================================


def test_risk_per_trade_cannot_be_zero():

    with pytest.raises(ValueError):

        RiskConfig(
            risk_per_trade=0
        )


def test_risk_per_trade_cannot_be_negative():

    with pytest.raises(ValueError):

        RiskConfig(
            risk_per_trade=-1
        )


def test_risk_per_trade_cannot_exceed_100():

    with pytest.raises(ValueError):

        RiskConfig(
            risk_per_trade=101
        )


def test_max_positions_must_be_positive():

    with pytest.raises(ValueError):

        RiskConfig(
            max_positions=0
        )


def test_commission_cannot_be_negative():

    with pytest.raises(ValueError):

        RiskConfig(
            commission=-1
        )


def test_slippage_cannot_be_negative():

    with pytest.raises(ValueError):

        RiskConfig(
            slippage=-0.5
        )