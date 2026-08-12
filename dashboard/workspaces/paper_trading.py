"""Paper trading workspace renderer."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.paper_trading import PaperTradingDataProvider
from tradepilotai_os.paper_trading import PaperTradingPage
from tradepilotai_os.paper_trading import PaperTradingService


def render_paper_trading_workspace(state: Any) -> None:
    """Render the paper trading workspace."""
    service = getattr(state, "paper_trading_service", None) if state is not None else None
    if not isinstance(service, PaperTradingService):
        service = PaperTradingService()
    PaperTradingPage(data_provider=PaperTradingDataProvider(service=service)).render()