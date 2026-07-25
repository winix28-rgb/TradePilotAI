"""
===========================================================
TradePilotAI
Market Configuration Tests
===========================================================
"""

import pytest

from models.market_config import MarketConfig


def test_default_values():

    config = MarketConfig()

    assert config.ticker == "RR.L"
    assert config.exchange == "LSE"
    assert config.timeframe == "1d"
    assert config.start_date == "2015-01-01"
    assert config.end_date == "2025-12-31"


def test_override_values():

    config = MarketConfig(
        ticker="VOD.L",
        exchange="LSE",
        timeframe="1h",
        start_date="2020-01-01",
        end_date="2025-01-01",
    )

    assert config.ticker == "VOD.L"
    assert config.exchange == "LSE"
    assert config.timeframe == "1h"
    assert config.start_date == "2020-01-01"
    assert config.end_date == "2025-01-01"


def test_config_is_immutable():

    config = MarketConfig()

    with pytest.raises(Exception):
        config.ticker = "TSCO.L"