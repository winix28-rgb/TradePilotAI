"""Trade history workspace renderer."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.trade_history import TradeHistoryDataProvider, TradeHistoryPage


def render_trade_history_workspace(state: Any) -> None:
    """Render the trade history workspace."""
    TradeHistoryPage(data_provider=TradeHistoryDataProvider()).render()
