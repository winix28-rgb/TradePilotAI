"""Domain models for the paper portfolio engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class PaperPosition:
    position_id: str
    symbol: str
    strategy_id: str
    strategy_name: str
    direction: str
    quantity: int
    entry_date: str = field(default_factory=_utc_now)
    entry_price: float = 0.0
    current_price: float = 0.0
    market_value: float = 0.0
    unrealised_pnl: float = 0.0
    unrealised_pnl_percent: float = 0.0
    todays_change: float = 0.0
    todays_change_percent: float = 0.0
    distance_to_stop_loss: float = 0.0
    distance_to_target: float = 0.0
    current_risk: float = 0.0
    days_open: int = 0
    last_updated: str = field(default_factory=_utc_now)
    risk: float = 0.0
    stop_loss: float = 0.0
    target: float = 0.0
    decision_id: str = ""
    status: str = "OPEN"
    price_status: str = "LIVE"
    price_stale: bool = False


@dataclass(slots=True)
class ClosedPaperTrade:
    trade_id: str
    position_id: str
    decision_id: str
    strategy_id: str
    strategy_name: str
    symbol: str
    direction: str
    entry_date: str
    exit_date: str = field(default_factory=_utc_now)
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: int = 0
    gross_profit: float = 0.0
    commission: float = 0.0
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    costs: float = 0.0
    net_profit: float = 0.0
    exit_reason: str = ""
    exit_explanation: str = ""
    holding_period: str = "0 days"
    holding_period_days: int = 0
    strategy: str = ""


@dataclass(slots=True)
class PortfolioStatistics:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    average_winner: float = 0.0
    average_loser: float = 0.0
    largest_winner: float = 0.0
    largest_loser: float = 0.0
    current_exposure: float = 0.0
    cash_allocation: float = 0.0
    invested_allocation: float = 0.0
    portfolio_return_percent: float = 0.0
    average_position_size: float = 0.0
    largest_position: float = 0.0
    smallest_position: float = 0.0


@dataclass(slots=True)
class PaperPortfolio:
    portfolio_id: str
    created_date: str
    cash: float
    buying_power: float
    portfolio_value: float
    realised_pnl: float = 0.0
    unrealised_pnl: float = 0.0
    total_pnl: float = 0.0
    open_positions: list[PaperPosition] = field(default_factory=list)
    closed_trades: list[ClosedPaperTrade] = field(default_factory=list)
    portfolio_statistics: PortfolioStatistics = field(default_factory=PortfolioStatistics)


PaperClosedTrade = ClosedPaperTrade
PaperStatistics = PortfolioStatistics