"""Position detail view for the TradePilotAI OS portfolio dashboard."""

from __future__ import annotations

from typing import Any


class PositionDetailPage:
    """Render a focused detail view for a selected position."""

    def __init__(self, position: Any | None = None) -> None:
        self.position = position

    def render(self) -> str:
        """Render the position detail page to a string."""

        if self.position is None:
            return "Position Detail\nNo position selected"

        metadata = getattr(self.position, "metadata", {}) or {}
        return "\n".join(
            [
                "Position Detail",
                f"Symbol: {getattr(self.position, 'symbol', 'UNKNOWN')}",
                f"Quantity: {getattr(self.position, 'quantity', 0)}",
                f"Entry Price: {getattr(self.position, 'average_price', 0.0)}",
                f"Current Price: {getattr(self.position, 'market_price', 0.0)}",
                f"Stop Loss: {metadata.get('stop_loss', 'N/A')}",
                f"Target: {metadata.get('target', 'N/A')}",
                f"Holding Time: {metadata.get('holding_time', 'N/A')}",
            ]
        )
