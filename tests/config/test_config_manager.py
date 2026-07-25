"""
===========================================================
TradePilotAI
Configuration Manager Tests
===========================================================
"""

from pathlib import Path

from config.config_manager import ConfigManager
from models.application_config import ApplicationConfig


def test_load_default_config():

    path = Path(
        "config/default_config.yaml"
    )

    config = ConfigManager.load(path)

    assert isinstance(config, ApplicationConfig)


def test_strategy_configuration():

    path = Path(
        "config/default_config.yaml"
    )

    config = ConfigManager.load(path)

    assert config.strategy.buy_rsi == 30
    assert config.strategy.exit_rsi == 50
    assert config.strategy.ema_fast == 12
    assert config.strategy.ema_slow == 26


def test_risk_configuration():

    path = Path(
        "config/default_config.yaml"
    )

    config = ConfigManager.load(path)

    assert config.risk.risk_per_trade == 1.0
    assert config.risk.max_positions == 10


def test_market_configuration():

    path = Path(
        "config/default_config.yaml"
    )

    config = ConfigManager.load(path)

    assert config.market.ticker == "RR.L"
    assert config.market.timeframe == "1d"


def test_backtest_configuration():

    path = Path(
        "config/default_config.yaml"
    )

    config = ConfigManager.load(path)

    assert config.backtest.starting_cash == 100000