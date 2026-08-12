"""Data provider for the paper trading Trade Journal workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .journal_service import JournalService
from .service import PaperTradingService


class JournalDataProvider:
    """Resolve trade journal data using journal + paper trading services."""

    def __init__(
        self,
        *,
        container: Container | None = None,
        journal_service: JournalService | None = None,
        paper_trading_service: PaperTradingService | None = None,
    ) -> None:
        self.container = container
        self.journal_service = journal_service
        self.paper_trading_service = paper_trading_service

    def get_trade_journal_data(
        self,
        *,
        filters: dict | None = None,
        search: str = "",
        sort_by: str = "exit_date",
        ascending: bool = False,
        selected_journal_id: str = "",
    ) -> dict[str, Any]:
        journal = self._resolve_journal_service()
        paper = self._resolve_paper_service()

        workspace = paper.get_workspace_data()
        journal.consume_events(workspace.get("audit_events", []))

        entries = journal.get_entries(filters=filters, search=search, sort_by=sort_by, ascending=ascending)
        summary = journal.get_summary(entries)

        selected_id = str(selected_journal_id or "")
        if not selected_id and entries:
            selected_id = str(entries[0].get("journal_id", ""))
        selected = journal.get_trade_detail(selected_id) if selected_id else {}

        return {
            "summary": summary,
            "entries": entries,
            "selected_journal_id": selected_id,
            "selected_trade": selected,
            "available_filters": self._available_filters(journal.get_entries()),
        }

    def save_note(self, journal_id: str, note: str) -> bool:
        journal = self._resolve_journal_service()
        return journal.set_note(str(journal_id), str(note))

    def export(
        self,
        *,
        format_name: str,
        filters: dict | None = None,
        search: str = "",
        sort_by: str = "exit_date",
        ascending: bool = False,
    ) -> tuple[bytes, str, str]:
        journal = self._resolve_journal_service()
        entries = journal.get_entries(filters=filters, search=search, sort_by=sort_by, ascending=ascending)
        return journal.export(format_name=format_name, entries=entries)

    def _resolve_journal_service(self) -> JournalService:
        service = self.journal_service
        if service is None and self.container is not None:
            try:
                service = self.container.resolve(JournalService)
            except Exception:
                service = None
        if service is None:
            service = JournalService()
            self.journal_service = service
        return service

    def _resolve_paper_service(self) -> PaperTradingService:
        service = self.paper_trading_service
        if service is None and self.container is not None:
            try:
                service = self.container.resolve(PaperTradingService)
            except Exception:
                service = None
        if service is None:
            service = PaperTradingService()
            self.paper_trading_service = service
        return service

    def _available_filters(self, entries: list[dict]) -> dict[str, list[str]]:
        strategies = sorted({str(item.get("strategy_name", "") or "") for item in entries if str(item.get("strategy_name", "") or "")})
        symbols = sorted({str(item.get("symbol", "") or "") for item in entries if str(item.get("symbol", "") or "")})
        directions = sorted({str(item.get("direction", "") or "") for item in entries if str(item.get("direction", "") or "")})
        exit_reasons = sorted({str(item.get("exit_reason", "") or "") for item in entries if str(item.get("exit_reason", "") or "")})

        return {
            "strategies": strategies,
            "symbols": symbols,
            "directions": directions,
            "exit_reasons": exit_reasons,
        }
