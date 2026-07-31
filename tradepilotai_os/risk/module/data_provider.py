"""Data provider for the Risk Dashboard workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .service import RiskDashboardService


class RiskDataProvider:
    """Resolve risk dashboard data from the dependency container."""

    def __init__(self, container: Container | None = None, service: RiskDashboardService | None = None) -> None:
        self.container = container
        self.service = service

    def get_risk_data(self) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            service = self.container.resolve(RiskDashboardService)
        if service is None:
            service = RiskDashboardService()

        snapshot = service.get_snapshot()
        return {
            "assessment": self._assessment_payload(snapshot.assessment),
            "exposures": [self._exposure_payload(item) for item in snapshot.exposures],
            "positions": [self._position_payload(item) for item in snapshot.positions],
            "rules": [self._rule_payload(item) for item in snapshot.rules],
            "violations": [self._violation_payload(item) for item in snapshot.violations],
            "timeline": snapshot.timeline,
            "events": [],
        }

    def _assessment_payload(self, assessment: Any) -> dict[str, Any]:
        return {
            "portfolio_risk_score": assessment.portfolio_risk_score,
            "total_exposure": assessment.total_exposure,
            "available_cash": assessment.available_cash,
            "buying_power": assessment.buying_power,
            "largest_position": assessment.largest_position,
            "daily_risk": assessment.daily_risk,
            "max_drawdown": assessment.max_drawdown,
            "value_at_risk": assessment.value_at_risk,
            "open_positions": assessment.open_positions,
            "summary": assessment.summary,
        }

    def _exposure_payload(self, exposure: Any) -> dict[str, Any]:
        return {"label": exposure.label, "value": exposure.value, "category": exposure.category}

    def _position_payload(self, position: Any) -> dict[str, Any]:
        return {
            "symbol": position.symbol,
            "position_size": position.position_size,
            "risk_percent": position.risk_percent,
            "stop_distance": position.stop_distance,
            "unrealised_pnl": position.unrealised_pnl,
            "exposure_percent": position.exposure_percent,
            "risk_rating": position.risk_rating,
        }

    def _rule_payload(self, rule: Any) -> dict[str, Any]:
        return {"name": rule.name, "current_value": rule.current_value, "configured_limit": rule.configured_limit, "status": rule.status}

    def _violation_payload(self, violation: Any) -> dict[str, Any]:
        return {"name": violation.name, "details": violation.details, "severity": violation.severity}
