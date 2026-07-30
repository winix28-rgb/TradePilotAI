"""
===========================================================
FTSE Quant Trader V2
Configuration Manager
===========================================================

Loads the strategy configuration from strategy.yaml.
"""

from pathlib import Path
import yaml


class ConfigManager:
    """
    Loads configuration settings from YAML.
    """

    def __init__(self):

        config_file = (
            Path(__file__).parent.parent
            / "config"
            / "strategy.yaml"
        )

        with open(config_file, "r") as file:
            self.config = yaml.safe_load(file)

        print("Configuration Loaded")

    @property
    def strategy(self):
        return self.config["strategy"]

    @property
    def risk(self):
        return self.config["risk"]

    @property
    def scanner(self):
        return self.config["scanner"]