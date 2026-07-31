"""Service layer for the Risk Dashboard workspace."""

from __future__ import annotations

from typing import Any

from .events import EventBus, RiskEvent
from .models import (
    PortfolioExposure,
    PositionRisk,
    RiskAssessment,
    RiskRule,
    RiskSnapshot,
    RiskViolation,
)


class RiskDashboardService:
    """Provide risk assessment data, rules, and event subscriptions."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus or EventBus()
        self._refresh_count = 0
        self._events: list[RiskEvent] = []

    def get_snapshot(self) -> RiskSnapshot:
        assessment = RiskAssessment(
            portfolio_risk_score=18.5,
            total_exposure=125000.0,
            available_cash=42000.0,
            buying_power=84000.0,
            largest_position="AAPL",
            daily_risk=3200.0,
            max_drawdown=-7.1,
            value_at_risk=5600.0,
            open_positions=4,
            summary="Balanced but watch volatility",
        )
        exposures = [
            PortfolioExposure(label="Technology", value=48000.0, category="Sector"),
            PortfolioExposure(label="Software", value=35000.0, category="Industry"),
            PortfolioExposure(label="AAPL", value=22000.0, category="Instrument"),
            PortfolioExposure(label="Long", value=78000.0, category="Direction"),
            PortfolioExposure(label="US", value=92000.0, category="Country"),
            PortfolioExposure(label="USD", value=125000.0, category="Currency"),
        ]
        positions = [
            PositionRisk(symbol="AAPL", position_size=120.0, risk_percent=2.4, stop_distance=5.5, unrealised_pnl=1400.0, exposure_percent=18.0, risk_rating="Medium"),
            PositionRisk(symbol="MSFT", position_size=80.0, risk_percent=1.8, stop_distance=4.0, unrealised_pnl=900.0, exposure_percent=12.0, risk_rating="Low"),
        ]
        rules = [
            RiskRule(name="Max Risk Per Trade", current_value=1.2, configured_limit=2.0, status="OK"),
            RiskRule(name="Max Portfolio Exposure", current_value=58.0, configured_limit=70.0, status="OK"),
            RiskRule(name="Max Open Positions", current_value=4.0, configured_limit=6.0, status="Warning"),
            RiskRule(name="Daily Loss Limit", current_value=3200.0, configured_limit=4000.0, status="OK"),
            RiskRule(name="Weekly Loss Limit", current_value=7800.0, configured_limit=10000.0, status="OK"),
        ]
        violations = [RiskViolation(name="Risk Limit Breached", details="Position size approaches policy limit", severity="Warning")]
        timeline = [
            {"event": "Position Opened", "time": "09:30"},
            {"event": "Risk Increased", "time": "10:10"},
            {"event": "Stop Updated", "time": "10:45"},
            {"event": "Drawdown Alert", "time": "11:20"},
        ]
        return RiskSnapshot(
            assessment=assessment,
            exposures=exposures,
            positions=positions,
            rules=rules,
            violations=violations,
            timeline=timeline,
        )

    def subscribe(self, event: RiskEvent) -> None:
        self._events.append(event)
        self.event_bus.publish(event.name, {"payload": event.payload})

    def refresh(self) -> None:
        self._refresh_count += 1

    def refresh_count(self) -> int:
        return self._refresh_count
