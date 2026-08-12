"""Trade journal workspace renderer."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.paper_trading import JournalDataProvider
from tradepilotai_os.paper_trading import JournalPage
from tradepilotai_os.paper_trading import JournalService
from tradepilotai_os.paper_trading import PaperTradingService


def render_trade_journal_workspace(state: Any) -> None:
    """Render the event-driven paper trading trade journal workspace."""
    journal_service = getattr(state, "trade_journal_service", None) if state is not None else None
    if not isinstance(journal_service, JournalService):
        journal_service = JournalService()
        if state is not None:
            if isinstance(state, dict):
                state["trade_journal_service"] = journal_service
            else:
                setattr(state, "trade_journal_service", journal_service)

    paper_service = getattr(state, "paper_trading_service", None) if state is not None else None
    if not isinstance(paper_service, PaperTradingService):
        paper_service = PaperTradingService(journal_service=journal_service)

    JournalPage(data_provider=JournalDataProvider(journal_service=journal_service, paper_trading_service=paper_service)).render()
