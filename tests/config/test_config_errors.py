"""
===========================================================
TradePilotAI
Configuration Error Tests
===========================================================
"""

from pathlib import Path

import pytest

from config.config_manager import ConfigManager
from config.exceptions import ConfigurationError


def test_missing_config_file():

    with pytest.raises(ConfigurationError):

        ConfigManager.load(
            "config/missing.yaml"
        )


def test_invalid_yaml(tmp_path):

    file = tmp_path / "bad.yaml"

    file.write_text(
        "strategy:\n"
        "  buy_rsi: ["
    )

    with pytest.raises(ConfigurationError):

        ConfigManager.load(file)


def test_invalid_strategy_configuration(tmp_path):

    file = tmp_path / "bad_strategy.yaml"

    file.write_text(
        """
strategy:
  buy_rsi: 200
"""
    )

    with pytest.raises(ConfigurationError):

        ConfigManager.load(file)


def test_invalid_risk_configuration(tmp_path):

    file = tmp_path / "bad_risk.yaml"

    file.write_text(
        """
risk:
  risk_per_trade: 200
"""
    )

    with pytest.raises(ConfigurationError):

        ConfigManager.load(file)