"""Domain models for the paper trading Trade Journal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DecisionSnapshot:
    """Immutable decision metrics captured at trade entry."""

    decision_score: float = 0.0
    confidence: float = 0.0
    technical_score: float = 0.0
    strategy_score: float = 0.0
    risk_score: float = 0.0
    portfolio_score: float = 0.0
    market_score: float = 0.0
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class RiskSnapshot:
    """Immutable risk controls captured for the trade."""

    risk_percent: float = 0.0
    position_size: float = 0.0
    capital_at_risk: float = 0.0
    reward_risk_ratio: float = 0.0
    stop_loss: float = 0.0
    target: float = 0.0


@dataclass(frozen=True, slots=True)
class PerformanceSnapshot:
    """Immutable portfolio and strategy performance state at close time."""

    win_loss: str = "LOSS"
    profit_factor_at_trade_time: float = 0.0
    running_equity: float = 0.0
    running_drawdown: float = 0.0
    strategy_win_rate: float = 0.0
    portfolio_win_rate: float = 0.0


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    """Immutable market context captured around trade execution."""

    timeframe: str = ""
    trend: str = ""
    rsi: float | None = None
    ema12: float | None = None
    ema26: float | None = None
    macd: float | None = None
    atr: float | None = None
    volume: float | None = None
    indicators: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """Immutable trade journal record produced by a close event."""

    journal_id: str
    trade_id: str
    position_id: str
    decision_id: str
    strategy_id: str
    strategy_name: str
    symbol: str
    asset_class: str
    direction: str
    entry_date: str
    exit_date: str
    holding_period: str
    entry_price: float
    exit_price: float
    quantity: int
    gross_profit: float
    costs: float
    net_profit: float
    return_percent: float
    exit_reason: str
    exit_explanation: str
    decision_snapshot: DecisionSnapshot
    risk_snapshot: RiskSnapshot
    performance_snapshot: PerformanceSnapshot
    market_snapshot: MarketSnapshot
    tags: tuple[str, ...] = field(default_factory=tuple)
    supporting_evidence: tuple[str, ...] = field(default_factory=tuple)
    audit_events: tuple[dict[str, Any], ...] = field(default_factory=tuple)
