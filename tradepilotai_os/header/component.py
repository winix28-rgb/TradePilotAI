"""Reusable header component for the TradePilotAI OS shell."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class Header:
    """Render a reusable application header with service-backed values."""

    def __init__(
        self,
        broker: Any | None = None,
        data_engine: Any | None = None,
        refresh_manager: Any | None = None,
        navigation_service: Any | None = None,
    ) -> None:
        self.broker = broker
        self.data_engine = data_engine
        self.refresh_manager = refresh_manager
        self.navigation_service = navigation_service

    def render(self) -> str:
        """Render the header with live or fallback values."""

        broker_status = self._get_broker_status()
        trading_mode = self._get_trading_mode()
        market_status = self._get_market_status()
        refresh_status = self._get_refresh_status()
        current_user = self._get_current_user()
        current_time = datetime.now(timezone.utc).strftime("%H:%M:%SZ")

        return "\n".join(
            [
                "TradePilotAI OS",
                f"Trading Mode: {trading_mode}",
                f"Broker Status: {broker_status}",
                f"Market Status: {market_status}",
                f"Current User: {current_user}",
                "Notifications: 🔔",
                f"Current Time: {current_time}",
                f"Refresh Status: {refresh_status}",
            ]
        )

    def _get_broker_status(self) -> str:
        if self.broker is None:
            return "Unavailable"
        if hasattr(self.broker, "connected"):
            return "Connected" if self.broker.connected else "Disconnected"
        return "Unavailable"

    def _get_trading_mode(self) -> str:
        if self.broker is None and self.data_engine is None:
            return "Unavailable"
        return "Paper" if self.broker is not None else "Standby"

    def _get_market_status(self) -> str:
        if self.data_engine is None:
            return "Unavailable"
        if hasattr(self.data_engine, "is_running"):
            return "Live" if self.data_engine.is_running() else "Idle"
        return "Unavailable"

    def _get_refresh_status(self) -> str:
        if self.refresh_manager is None:
            return "Unavailable"
        if hasattr(self.refresh_manager, "current_mode"):
            return str(self.refresh_manager.current_mode)
        return "Unavailable"

    def _get_current_user(self) -> str:
        if self.navigation_service is not None and hasattr(self.navigation_service, "current_route"):
            return self.navigation_service.current_route() or "Guest"
        return "Guest"
