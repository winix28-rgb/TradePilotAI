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