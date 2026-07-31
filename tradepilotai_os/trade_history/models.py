"""Domain models for the Trade History workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Trade:
    """Represents a single trade with lifecycle and execution details."""

    trade_id: str
    symbol: str
    company: str
    direction: str
    quantity: int
    entry_price: float
    exit_price: float | None = None
    entry_time: str | None = None
    exit_time: str | None = None
    duration: str | None = None
    gross_pnl: float | None = None
    net_pnl: float | None = None
    status: str = "Detected"
    strategy: str = "EMA/RSI"
    exit_reason: str | None = None
    entry_reason: str | None = None
    risk_assessment: str | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    commission: float | None = None
    slippage: float | None = None
    position_sizing: float | None = None
    notes: str = "Placeholder"
    account: str = "Paper"
    timeline: list[dict[str, Any]] = field(default_factory=list)
    related_events: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TradeSummary:
    """High-level summary metrics for the trade history workspace."""

    total_trades: int = 0
    open_trades: int = 0
    closed_trades: int = 0
    win_rate: str = "0%"
    net_profit: str = "$0"
    average_win: str = "$0"
    average_loss: str = "$0"
    profit_factor: str = "0.00"
    largest_win: str = "$0"
    largest_loss: str = "$0"


@dataclass(slots=True)
class TradeStatistics:
    """Support metrics for filtering and analytics."""

    total_trades: int = 0
    win_rate: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0


@dataclass(slots=True)
class TradeTimeline:
    """Represents the lifecycle timeline of a trade."""

    trade_id: str
    events: list[dict[str, Any]] = field(default_factory=list)
