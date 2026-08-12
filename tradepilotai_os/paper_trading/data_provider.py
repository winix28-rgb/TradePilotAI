"""Data provider for the Paper Trading workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .journal_data_provider import JournalDataProvider
from .service import PaperTradingService


class PaperTradingDataProvider:
    """Resolve paper-trading workspace data from the dependency container."""

    def __init__(self, container: Container | None = None, service: PaperTradingService | None = None) -> None:
        self.container = container
        self.service = service

    def get_paper_trading_data(self) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            try:
                service = self.container.resolve(PaperTradingService)
            except Exception:
                service = None
        if service is None:
            service = PaperTradingService()
        return service.get_workspace_data()

    def refresh(self) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            try:
                service = self.container.resolve(PaperTradingService)
            except Exception:
                service = None
        if service is None:
            service = PaperTradingService()
        return service.refresh_portfolio()

    def close_position(self, position_id: str, reason: str = "MANUAL_EXIT", explanation: str = "") -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            try:
                service = self.container.resolve(PaperTradingService)
            except Exception:
                service = None
        if service is None:
            service = PaperTradingService()

        service.manual_exit(position_id, reason=reason, explanation=explanation)
        return service.get_workspace_data()

    def get_trade_journal_data(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str = "",
        sort_by: str = "exit_date",
        ascending: bool = False,
        selected_journal_id: str = "",
    ) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            try:
                service = self.container.resolve(PaperTradingService)
            except Exception:
                service = None
        if service is None:
            service = PaperTradingService()

        provider = JournalDataProvider(container=self.container, journal_service=service.journal_service, paper_trading_service=service)
        return provider.get_trade_journal_data(
            filters=filters,
            search=search,
            sort_by=sort_by,
            ascending=ascending,
            selected_journal_id=selected_journal_id,
        )