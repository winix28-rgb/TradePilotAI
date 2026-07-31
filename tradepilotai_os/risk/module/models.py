"""Domain models for the Risk Dashboard workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RiskAssessment:
    """High-level portfolio and position risk assessment."""

    portfolio_risk_score: float = 0.0
    total_exposure: float = 0.0
    available_cash: float = 0.0
    buying_power: float = 0.0
    largest_position: str = "N/A"
    daily_risk: float = 0.0
    max_drawdown: float = 0.0
    value_at_risk: float = 0.0
    open_positions: int = 0
    summary: str = "Stable"


@dataclass(slots=True)
class PortfolioExposure:
    """Represents exposure broken down by segment."""

    label: str
    value: float
    category: str


@dataclass(slots=True)
class PositionRisk:
    """Represents an individual position's risk profile."""

    symbol: str
    position_size: float
    risk_percent: float
    stop_distance: float
    unrealised_pnl: float
    exposure_percent: float
    risk_rating: str


@dataclass(slots=True)
class RiskRule:
    """A configured risk rule with current and configured values."""

    name: str
    current_value: float
    configured_limit: float
    status: str = "OK"


@dataclass(slots=True)
class RiskViolation:
    """Represents a breach or warning condition."""

    name: str
    details: str
    severity: str = "Warning"


@dataclass(slots=True)
class RiskSnapshot:
    """Represents the full risk snapshot for the workspace."""

    assessment: RiskAssessment
    exposures: list[PortfolioExposure] = field(default_factory=list)
    positions: list[PositionRisk] = field(default_factory=list)
    rules: list[RiskRule] = field(default_factory=list)
    violations: list[RiskViolation] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
