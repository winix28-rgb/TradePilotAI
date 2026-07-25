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


# =========================================================
# Validation Tests
# =========================================================


def test_starting_cash_cannot_be_zero():

    with pytest.raises(ValueError):

        BacktestConfig(
            starting_cash=0
        )


def test_starting_cash_cannot_be_negative():

    with pytest.raises(ValueError):

        BacktestConfig(
            starting_cash=-1000
        )


def test_benchmark_cannot_be_empty():

    with pytest.raises(ValueError):

        BacktestConfig(
            benchmark=""
        )