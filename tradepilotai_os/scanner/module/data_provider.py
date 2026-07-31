"""Data provider for the scanner workspace page."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .service import ScannerService


class ScannerDataProvider:
    """Resolve scanner data from the app container."""

    def __init__(self, container: Container | None = None, scanner_service: ScannerService | None = None) -> None:
        self.container = container
        self.scanner_service = scanner_service

    def get_scanner_data(self) -> dict[str, Any]:
        service = self.scanner_service
        if service is None and self.container is not None:
            service = self.container.resolve(ScannerService)
        if service is None:
            service = ScannerService()
        return service.scan()
