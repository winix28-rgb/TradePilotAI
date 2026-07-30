"""
===========================================================
TradePilotAI Operating System
Configuration Manager
===========================================================
"""

from pathlib import Path
from typing import Any

import json


class ConfigurationManager:
    """
    Central configuration storage.
    """

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}

    def load(self, filename: str) -> None:

        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(filename)

        with open(path, "r", encoding="utf-8") as file:
            self._config = json.load(file)

    def save(self, filename: str) -> None:

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self._config, file, indent=4)

    def get(self, key: str, default: Any = None) -> Any:

        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:

        self._config[key] = value

    def exists(self, key: str) -> bool:

        return key in self._config

    def clear(self) -> None:

        self._config.clear()