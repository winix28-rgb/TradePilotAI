"""Validation result models for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    """Represents one deterministic validation assertion."""

    name: str
    passed: bool
    expected: str
    actual: str
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "expected": self.expected,
            "actual": self.actual,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class ValidationModuleResult:
    """Represents the outcome of one validation module."""

    name: str
    checks: list[ValidationCheck] = field(default_factory=list)
    status: str = "FAIL"
    score: float = 0.0
    summary: str = ""

    @property
    def passed_checks(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "checks": [check.to_dict() for check in self.checks],
            "status": self.status,
            "score": self.score,
            "summary": self.summary,
            "passed_checks": self.passed_checks,
            "total_checks": self.total_checks,
        }


@dataclass(frozen=True, slots=True)
class ValidationSuiteResult:
    """Represents the full validation workspace result."""

    modules: list[ValidationModuleResult] = field(default_factory=list)
    overall_status: str = "FAIL"
    overall_score: float = 0.0
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    summary: str = ""

    @property
    def passed_modules(self) -> int:
        return sum(1 for module in self.modules if module.status == "PASS")

    @property
    def total_modules(self) -> int:
        return len(self.modules)

    @property
    def passed_checks(self) -> int:
        return sum(module.passed_checks for module in self.modules)

    @property
    def total_checks(self) -> int:
        return sum(module.total_checks for module in self.modules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "modules": [module.to_dict() for module in self.modules],
            "overall_status": self.overall_status,
            "overall_score": self.overall_score,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "passed_modules": self.passed_modules,
            "total_modules": self.total_modules,
            "passed_checks": self.passed_checks,
            "total_checks": self.total_checks,
        }