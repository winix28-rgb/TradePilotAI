"""
===========================================================
TradePilotAI
IG Configuration
===========================================================

Stores IG Markets connection settings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IGConfig:
    """
    IG Markets API configuration.
    """

    username: str

    password: str

    api_key: str

    account_type: str = "DEMO"


    def __post_init__(self):

        if not self.username:
            raise ValueError(
                "IG username cannot be empty"
            )

        if not self.password:
            raise ValueError(
                "IG password cannot be empty"
            )

        if not self.api_key:
            raise ValueError(
                "IG API key cannot be empty"
            )

