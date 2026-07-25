"""
===========================================================
TradePilotAI
Configuration Manager
===========================================================

Loads YAML configuration files and converts them into
strongly typed application configuration objects.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from config.exceptions import ConfigurationError

from models.application_config import ApplicationConfig
from models.backtest_config import BacktestConfig
from models.market_config import MarketConfig
from models.risk_config import RiskConfig
from models.strategy_config import StrategyConfig


class ConfigManager:
    """
    Handles loading application configuration.
    """

    @staticmethod
    def load(
        path: str | Path,
    ) -> ApplicationConfig:
        """
        Load configuration from YAML.
        """

        config_path = Path(path)

        if not config_path.exists():

            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )

        try:

            with config_path.open("r") as file:
                data = yaml.safe_load(file)

        except yaml.YAMLError as error:

            raise ConfigurationError(
                "Invalid YAML configuration"
            ) from error

        try:

            return ApplicationConfig(

                strategy=StrategyConfig(
                    **data.get("strategy", {})
                ),

                risk=RiskConfig(
                    **data.get("risk", {})
                ),

                backtest=BacktestConfig(
                    **data.get("backtest", {})
                ),

                market=MarketConfig(
                    **data.get("market", {})
                ),
            )

        except (TypeError, ValueError) as error:

            raise ConfigurationError(
                f"Invalid configuration: {error}"
            ) from error