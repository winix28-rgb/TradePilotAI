"""
===========================================================
TradePilotAI
Configuration Settings
Version 4.0
===========================================================

Central application configuration.

Contains:
- Strategy settings
- Risk settings
- Backtest settings
- Runtime environment settings
"""

from __future__ import annotations

import os

from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


# ==========================================================
# ACCOUNT SETTINGS
# ==========================================================

ACCOUNT_SIZE = 100000

RISK_PER_TRADE = 0.01

MAX_OPEN_POSITIONS = 10

COMMISSION = 0.0

SLIPPAGE = 0.0


# ==========================================================
# INDICATORS
# ==========================================================

EMA_FAST = 12

EMA_SLOW = 26

RSI_PERIOD = 14


# ==========================================================
# STRATEGY
# ==========================================================

BUY_RSI = 30

SELL_RSI = 70

EXIT_RSI = 50

SETUP_TIMEOUT = 10


# ==========================================================
# BACKTEST
# ==========================================================

START_DATE = "2015-01-01"

END_DATE = "2030-01-01"

DEFAULT_MARKET = "FTSE100"


# ==========================================================
# REPORTING
# ==========================================================

SHOW_DEBUG = True

SAVE_TRADE_LOG = True

SAVE_REPORT = True



# ==========================================================
# RUNTIME SETTINGS
# ==========================================================

@dataclass(
    frozen=True,
    slots=True,
)
class Settings:
    """
    Runtime application settings.
    """

    mode: str

    ig_username: str | None

    ig_password: str | None

    ig_api_key: str | None

    ig_account_type: str


    @classmethod
    def load(cls):
        """
        Load settings from environment.
        """

        return cls(

            mode=os.getenv(
                "TRADEPILOT_MODE",
                "BACKTEST",
            ),

            ig_username=os.getenv(
                "IG_USERNAME"
            ),

            ig_password=os.getenv(
                "IG_PASSWORD"
            ),

            ig_api_key=os.getenv(
                "IG_API_KEY"
            ),

            ig_account_type=os.getenv(
                "IG_ACCOUNT_TYPE",
                "DEMO",
            ),
        )