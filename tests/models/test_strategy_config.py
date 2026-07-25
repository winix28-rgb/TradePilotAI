"""
===========================================================
TradePilotAI
Strategy Config Tests
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