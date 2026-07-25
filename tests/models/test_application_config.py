"""
===========================================================
TradePilotAI
Application Configuration Tests
===========================================================
"""

import pytest

from models.application_config import ApplicationConfig
from models.strategy_config import StrategyConfig
from models.risk_config import RiskConfig
from models.backtest_config import BacktestConfig
from models.market_config import MarketConfig


def test_default_configuration():

    config = ApplicationConfig()

    assert isinstance(config.strategy, StrategyConfig)
    assert isinstance(config.risk, RiskConfig)
    assert isinstance(config.backtest, BacktestConfig)
    assert isinstance(config.market, MarketConfig)


def test_override_sections():

    strategy = StrategyConfig(buy_rsi=28)

    risk = RiskConfig(max_positions=5)

    config = ApplicationConfig(
        strategy=strategy,
        risk=risk,
    )

    assert config.strategy.buy_rsi == 28
    assert config.risk.max_positions == 5
    assert config.backtest.starting_cash == 100_000.0
    assert config.market.ticker == "RR.L"


def test_application_config_is_immutable():

    config = ApplicationConfig()

    with pytest.raises(Exception):
        config.strategy = StrategyConfig()