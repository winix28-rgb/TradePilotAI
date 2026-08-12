"""Performance workspace renderer."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.performance import PerformanceDataProvider
from tradepilotai_os.performance import PerformancePage


def render_performance_workspace(state: Any) -> None:
    """Render the professional read-only performance workspace."""
    def _from_state(name: str) -> Any:
        if state is None:
            return None
        if isinstance(state, dict):
            return state.get(name)
        return getattr(state, name, None)

    provider_state = {
        "paper_trading_service": _from_state("paper_trading_service"),
        "trade_journal_service": _from_state("trade_journal_service"),
    }
    PerformancePage(data_provider=PerformanceDataProvider(state=provider_state)).render()
