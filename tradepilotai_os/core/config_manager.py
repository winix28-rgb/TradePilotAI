"""
============================================================
TradePilotAI Operating System
Configuration Manager
============================================================

A configuration manager that fits the TradePilotAI OS
architecture by extending the central JSON-backed
configuration store with section-based accessors for
application and trading settings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import ConfigurationManager as BaseConfigurationManager


class ConfigManager(BaseConfigurationManager):
    """
    Configuration manager for TradePilotAI OS.

    This keeps configuration storage centralized in the OS
    architecture while exposing a simple section-based API
    similar to the earlier trading prototype.
    """

    def __init__(self, filename: str | None = None) -> None:
        super().__init__()
        self._filename: str | None = None

        if filename is not None:
            self.load(filename)

    @property
    def filename(self) -> str | None:
        return self._filename

    def load(self, filename: str) -> None:
        """
        Load configuration from a JSON or YAML file.
        """

        path = Path(filename)

        if not path.is_absolute():
            path = Path.cwd() / path

        if not path.exists():
            raise FileNotFoundError(str(path))

        with path.open("r", encoding="utf-8") as handle:
            config_data = self._parse_config(path, handle)

        if not isinstance(config_data, dict):
            raise ValueError("Configuration root must be an object.")

        self._config = config_data
        self._filename = str(path)

    def save(self, filename: str) -> None:
        """
        Save the current configuration to disk.
        """

        path = Path(filename)

        if not path.is_absolute():
            path = Path.cwd() / path

        with path.open("w", encoding="utf-8") as handle:
            json.dump(self._config, handle, indent=4)

        self._filename = str(path)

    def section(self, name: str, default: Any = None) -> Any:
        """
        Return a configuration section by name.
        """

        return self.get(name, default)

    @property
    def strategy(self) -> dict[str, Any]:
        return self.get("strategy", {})

    @property
    def risk(self) -> dict[str, Any]:
        return self.get("risk", {})

    @property
    def scanner(self) -> dict[str, Any]:
        return self.get("scanner", {})

    @staticmethod
    def _parse_config(path: Path, handle) -> Any:
        suffix = path.suffix.lower()

        if suffix in {".json"}:
            return json.load(handle)

        if suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise ImportError(
                    "PyYAML is required to load YAML configuration files."
                ) from exc

            return yaml.safe_load(handle)

        try:
            return json.load(handle)
        except json.JSONDecodeError:
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise ImportError(
                    "Unable to parse configuration file; install PyYAML for YAML support."
                ) from exc

            return yaml.safe_load(handle)
