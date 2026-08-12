"""Domain models for the professional performance dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TradeRecord:
    """Normalized read-only trade record used by the performance engine."""

    source: str
    trade_id: str
    strategy_id: str
    strategy_name: str
    symbol: str
    asset_class: str
    direction: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: float
    gross_profit: float
    gross_loss: float
    costs: float
    net_profit: float
    exit_reason: str
    holding_hours: float
    risk_percent: float
    capital_at_risk: float
    position_size: float


@dataclass(slots=True)
class PerformanceDashboard:
    """Structured output consumed by the performance workspace UI."""

    generated_at: str
    portfolio_overview: dict[str, Any] = field(default_factory=dict)
    performance_kpis: dict[str, Any] = field(default_factory=dict)
    equity_curve: dict[str, Any] = field(default_factory=dict)
    drawdown: dict[str, Any] = field(default_factory=dict)
    trade_analysis: dict[str, Any] = field(default_factory=dict)
    strategy_analysis: list[dict[str, Any]] = field(default_factory=list)
    exit_analysis: list[dict[str, Any]] = field(default_factory=list)
    time_analysis: dict[str, Any] = field(default_factory=dict)
    long_short_analysis: dict[str, Any] = field(default_factory=dict)
    asset_analysis: list[dict[str, Any]] = field(default_factory=list)
    risk_analysis: dict[str, Any] = field(default_factory=dict)
    charts: dict[str, Any] = field(default_factory=dict)
    trades: list[dict[str, Any]] = field(default_factory=list)
    sources: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "portfolio_overview": self.portfolio_overview,
            "performance_kpis": self.performance_kpis,
            "equity_curve": self.equity_curve,
            "drawdown": self.drawdown,
            "trade_analysis": self.trade_analysis,
            "strategy_analysis": self.strategy_analysis,
            "exit_analysis": self.exit_analysis,
            "time_analysis": self.time_analysis,
            "long_short_analysis": self.long_short_analysis,
            "asset_analysis": self.asset_analysis,
            "risk_analysis": self.risk_analysis,
            "charts": self.charts,
            "trades": self.trades,
            "sources": self.sources,
        }
