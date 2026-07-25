"""
===========================================================
TradePilotAI
Backtest Configuration Tests
===========================================================
"""

import pytest

from models.backtest_config import BacktestConfig


def test_default_values():

    config = BacktestConfig()

    assert config.starting_cash == 100_000.0
    assert config.benchmark == "FTSE100"
    assert config.reinvest_profits is True
    assert config.allow_fractional_shares is False


def test_override_values():

    config = BacktestConfig(
        starting_cash=250_000.0,
        benchmark="SP500",
        reinvest_profits=False,
        allow_fractional_shares=True,
    )

    assert config.starting_cash == 250_000.0
    assert config.benchmark == "SP500"
    assert config.reinvest_profits is False
    assert config.allow_fractional_shares is True


def test_config_is_immutable():

    config = BacktestConfig()

    with pytest.raises(Exception):
        config.starting_cash = 50_000.0