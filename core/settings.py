"""
===========================================================
TradePilotAI
Application Settings
===========================================================

Loads environment configuration.
"""

from __future__ import annotations

import os

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """
    Application runtime settings.
    """

    mode: str

    ig_username: str | None

    ig_password: str | None

    ig_api_key: str | None

    ig_account_type: str


    @classmethod
    def load(cls):

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