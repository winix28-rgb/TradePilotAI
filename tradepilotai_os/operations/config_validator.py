"""Configuration validation for TradePilotAI OS."""

from __future__ import annotations

from typing import Any


class ConfigurationValidator:
    """Validate operational configuration values before startup."""

    def __init__(self, config_manager: Any | None = None) -> None:
        self.config_manager = config_manager

    def validate(self) -> list[str]:
        if self.config_manager is None:
            return ["Configuration manager is missing."]

        errors: list[str] = []
        risk = self.config_manager.get("risk", {})
        if not isinstance(risk, dict):
            errors.append("Risk settings must be a mapping.")
        else:
            for key in ["risk_per_trade", "max_position_size"]:
                if key not in risk:
                    errors.append(f"Risk setting missing: {key}")

        strategy = self.config_manager.get("strategy", {})
        if not isinstance(strategy, dict):
            errors.append("Strategy settings must be a mapping.")
        else:
            for key in ["rsi_period", "ema_fast", "ema_slow"]:
                if key not in strategy:
                    errors.append(f"Strategy setting missing: {key}")

        broker = self.config_manager.get("broker", {})
        if not isinstance(broker, dict):
            errors.append("Broker settings must be a mapping.")
        elif broker.get("type") not in {"paper", "live", "mock"}:
            errors.append("Broker type must be paper, live, or mock.")

        portfolio = self.config_manager.get("portfolio", {})
        if not isinstance(portfolio, dict):
            errors.append("Portfolio settings must be a mapping.")

        refresh = self.config_manager.get("refresh", {})
        if not isinstance(refresh, dict):
            errors.append("Refresh settings must be a mapping.")
        elif int(refresh.get("interval_seconds", 0)) <= 0:
            errors.append("Refresh interval must be greater than zero.")

        environment = self.config_manager.get("environment", {})
        if not isinstance(environment, dict):
            errors.append("Environment settings must be a mapping.")

        return errors
