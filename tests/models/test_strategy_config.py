"""
===========================================================
TradePilotAI
Strategy Configuration Tests
===========================================================
"""

import pytest

from models.strategy_config import StrategyConfig


def test_default_values():

    config = StrategyConfig()

    assert config.buy_rsi == 30
    assert config.exit_rsi == 50
    assert config.ema_fast == 12
    assert config.ema_slow == 26


def test_override_single_value():

    config = StrategyConfig(
        buy_rsi=28
    )

    assert config.buy_rsi == 28
    assert config.exit_rsi == 50
    assert config.ema_fast == 12
    assert config.ema_slow == 26


def test_override_multiple_values():

    config = StrategyConfig(
        buy_rsi=25,
        exit_rsi=55,
        ema_fast=10,
        ema_slow=30,
    )

    assert config.buy_rsi == 25
    assert config.exit_rsi == 55
    assert config.ema_fast == 10
    assert config.ema_slow == 30


def test_config_is_immutable():

    config = StrategyConfig()

    with pytest.raises(Exception):
        config.buy_rsi = 20


# =========================================================
# Validation Tests
# =========================================================


def test_invalid_buy_rsi():

    with pytest.raises(ValueError):

        StrategyConfig(
            buy_rsi=120
        )


def test_invalid_exit_rsi():

    with pytest.raises(ValueError):

        StrategyConfig(
            exit_rsi=-5
        )


def test_invalid_fast_ema():

    with pytest.raises(ValueError):

        StrategyConfig(
            ema_fast=0
        )


def test_invalid_slow_ema():

    with pytest.raises(ValueError):

        StrategyConfig(
            ema_slow=0
        )


def test_fast_ema_cannot_equal_slow_ema():

    with pytest.raises(ValueError):

        StrategyConfig(
            ema_fast=26,
            ema_slow=26
        )


def test_fast_ema_cannot_exceed_slow_ema():

    with pytest.raises(ValueError):

        StrategyConfig(
            ema_fast=30,
            ema_slow=10
        )