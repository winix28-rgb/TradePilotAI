"""Logging service."""

from tradepilotai_os.core.service import Service


class LoggingService(Service):
    """Simple logging service."""

    @property
    def name(self) -> str:
        return "Logging"

    def start(self) -> None:
        print("✓ Logging Ready")

    def stop(self) -> None:
        print("Logging Stopped")