"""
===========================================================
TradePilotAI Operating System
Environment Manager
===========================================================

Provides access to operating system environment variables
and application configuration.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class EnvironmentManager:
    """
    Loads and manages environment variables.

    Future versions will merge:

    - .env
    - config.json
    - user profiles
    - encrypted secrets
    """

    def __init__(self, env_file: str = ".env") -> None:

        self.root = Path.cwd()
        self.env_path = self.root / env_file

        if load_dotenv and self.env_path.exists():
            load_dotenv(self.env_path)

    def get(
        self,
        key: str,
        default=None,
    ):
        """
        Return an environment variable.
        """
        return os.getenv(key, default)

    def get_int(
        self,
        key: str,
        default: int = 0,
    ) -> int:

        try:
            return int(self.get(key, default))
        except (TypeError, ValueError):
            return default

    def get_float(
        self,
        key: str,
        default: float = 0.0,
    ) -> float:

        try:
            return float(self.get(key, default))
        except (TypeError, ValueError):
            return default

    def get_bool(
        self,
        key: str,
        default: bool = False,
    ) -> bool:

        value = str(self.get(key, default)).lower()

        return value in (
            "1",
            "true",
            "yes",
            "on",
        )

    def exists(self, key: str) -> bool:
        """
        Check if an environment variable exists.
        """
        return key in os.environ

    def as_dict(self) -> dict:
        """
        Return all environment variables.
        """
        return dict(os.environ)