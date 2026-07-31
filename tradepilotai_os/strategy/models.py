"""Domain models for the Strategy Centre workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StrategyConfiguration:
    """Represents configurable strategy parameters."""

    rsi_period: int = 14
    rsi_buy_level: float = 30.0
    rsi_sell_level: float = 70.0
    ema_fast: int = 9
    ema_slow: int = 21
    risk_per_trade: float = 0.01
    max_positions: int = 3
    reward_risk: float = 2.0
    stop_loss: float = 0.02
    take_profit: float = 0.04
    execution_mode: str = "Paper"


@dataclass(slots=True)
class StrategyPerformance:
    """Represents summary metrics for a strategy version."""

    backtest_return: float = 0.0
    paper_return: float = 0.0
    live_return: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0


@dataclass(slots=True)
class StrategyVersion:
    """Represents a versioned snapshot of a strategy."""

    version: str
    date: str
    author: str
    notes: str
    configuration: StrategyConfiguration = field(default_factory=StrategyConfiguration)
    performance: StrategyPerformance = field(default_factory=StrategyPerformance)


@dataclass(slots=True)
class Strategy:
    """Represents a strategy managed by the Strategy Centre."""

    name: str
    version: str
    description: str
    status: str = "Draft"
    markets: str = "FX"
    timeframe: str = "1H"
    created_date: str = "2026-01-01"
    last_modified: str = "2026-01-01"
    configuration: StrategyConfiguration = field(default_factory=StrategyConfiguration)
    performance: StrategyPerformance = field(default_factory=StrategyPerformance)
    versions: list[StrategyVersion] = field(default_factory=list)
    deployment: "StrategyDeployment | None" = None


@dataclass(slots=True)
class StrategyDeployment:
    """Represents a deployment target for a strategy."""

    target: str
    status: str = "Pending"
    deployed_at: str | None = None
    broker_interface: str = "Broker Interface"
    orchestrator: str = "Application Orchestrator"
    metadata: dict[str, Any] = field(default_factory=dict)
