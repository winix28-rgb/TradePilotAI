"""Portfolio manager for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tradepilotai_os.models.trade import Trade
from .position import Position


@dataclass(slots=True)
class PortfolioState:
    """Snapshot of the portfolio account state."""

    cash: float = 0.0
    realised_pnl: float = 0.0
    unrealised_pnl: float = 0.0
    exposure: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)


class PortfolioManager:
    """Manage portfolio positions and account-level metrics.

    This layer receives risk-approved trades and tracks them as
    positions, cash, and P&L. It does not interact with scanners,
    strategy logic, or market access modules directly.
    """

    def __init__(self, initial_cash: float = 0.0) -> None:
        self.state = PortfolioState(cash=initial_cash)

    def add_trade(self, trade: Trade, market_price: float | None = None) -> None:
        """Record a trade into the portfolio state."""

        if trade.entry_price is None:
            return

        if trade.direction == "LONG":
            position = self.state.positions.get(trade.ticker)
            if position is None:
                position = Position(symbol=trade.ticker)
                self.state.positions[trade.ticker] = position

            position.quantity += 1
            position.average_price = (
                (position.average_price * (position.quantity - 1)) + trade.entry_price
            ) / position.quantity
            position.market_price = market_price or trade.entry_price
            position.exposure = position.quantity * position.market_price
            self.state.exposure += position.exposure

        self.state.cash -= trade.entry_price

    def mark_to_market(self, symbol: str, market_price: float) -> None:
        """Update the unrealised P&L for a position."""

        position = self.state.positions.get(symbol)
        if position is None:
            return

        position.market_price = market_price
        position.exposure = position.quantity * market_price
        self.state.exposure = sum(item.exposure for item in self.state.positions.values())

        if position.quantity != 0:
            self.state.unrealised_pnl = (
                (market_price - position.average_price) * position.quantity
            )

    def close_position(self, symbol: str, market_price: float) -> None:
        """Close a position and realise P&L."""

        position = self.state.positions.get(symbol)
        if position is None:
            return

        realised = (market_price - position.average_price) * position.quantity
        self.state.realised_pnl += realised
        self.state.cash += market_price * position.quantity

        position.quantity = 0
        position.average_price = 0.0
        position.market_price = market_price
        position.exposure = 0.0
        self.state.exposure = sum(item.exposure for item in self.state.positions.values())
        self.state.unrealised_pnl = 0.0

    def get_position(self, symbol: str) -> Position | None:
        """Return the current position for a symbol if it exists."""

        return self.state.positions.get(symbol)
