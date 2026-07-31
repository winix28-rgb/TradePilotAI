"""Startup validation for TradePilotAI OS."""

from __future__ import annotations

from typing import Any


class StartupValidator:
    """Validate configuration and registrations before startup."""

    def __init__(self, config_manager: Any | None = None, container: Any | None = None, navigation_service: Any | None = None) -> None:
        self.config_manager = config_manager
        self.container = container
        self.navigation_service = navigation_service
        self.errors: list[str] = []

    def validate(self) -> list[str]:
        self.errors = []
        if self.config_manager is None:
            self.errors.append("Configuration manager is missing.")
        else:
            self._validate_config()
        if self.container is None:
            self.errors.append("Dependency injection container is missing.")
        else:
            self._validate_container()
        if self.navigation_service is None:
            self.errors.append("Navigation service is missing.")
        else:
            self._validate_navigation()
        return self.errors

    def _validate_config(self) -> None:
        if self.config_manager.get("risk") is None:
            self.errors.append("Risk settings missing.")
        if self.config_manager.get("broker") is None:
            self.errors.append("Broker settings missing.")
        if self.config_manager.get("strategy") is None:
            self.errors.append("Strategy settings missing.")
        if self.config_manager.get("portfolio") is None:
            self.errors.append("Portfolio settings missing.")
        if self.config_manager.get("refresh") is None:
            self.errors.append("Refresh settings missing.")

    def _validate_container(self) -> None:
        required = ["config", "broker", "container", "notifications", "refresh_manager"]
        for name in required:
            if not self.container.contains(name):
                self.errors.append(f"Required service not registered: {name}")

    def _validate_navigation(self) -> None:
        for route in ["portfolio", "scanner", "backtesting", "trade_history", "risk", "live_trading", "strategy"]:
            if route not in self.navigation_service._routes:
                self.errors.append(f"Navigation route missing: {route}")
