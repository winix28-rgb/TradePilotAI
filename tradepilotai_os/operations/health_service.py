"""Health check service for TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HealthStatus:
    name: str
    status: str = "READY"
    details: dict[str, Any] = field(default_factory=dict)


class HealthCheckService:
    """Aggregate readiness checks for platform components."""

    def __init__(self) -> None:
        self._checks: dict[str, HealthStatus] = {}

    def register(self, name: str, status: str, details: dict[str, Any] | None = None) -> None:
        self._checks[name] = HealthStatus(name=name, status=status, details=details or {})

    def get(self, name: str) -> HealthStatus | None:
        return self._checks.get(name)

    def overall_status(self) -> str:
        if not self._checks:
            return "READY"
        statuses = [check.status for check in self._checks.values()]
        if "FAILED" in statuses:
            return "FAILED"
        if "WARNING" in statuses:
            return "WARNING"
        return "READY"

    def report(self) -> dict[str, Any]:
        return {
            "overall_status": self.overall_status(),
            "checks": {name: {"status": item.status, "details": item.details} for name, item in self._checks.items()},
        }
