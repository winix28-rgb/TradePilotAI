"""Live trading workspace renderer."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.live_trading import LiveTradingDataProvider, LiveTradingPage


def render_live_trading_workspace(state: Any) -> None:
    """Render the live trading workspace."""
    LiveTradingPage(data_provider=LiveTradingDataProvider()).render()
