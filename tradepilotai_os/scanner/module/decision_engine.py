"""Decision engine framework for scanner opportunity assessments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class AssessmentComponent(Protocol):
    """Minimal interface expected from assessment score components."""

    score: float
    confidence: float
    coverage: float
    explanation: dict[str, float]


@dataclass(frozen=True)
class DecisionThresholds:
    """Decision Rule Book v1.0 threshold configuration."""

    minimum_coverage: float = 0.60
    reject_risk_score: float = 40.0
    reject_strategy_score: float = 50.0
    watch_portfolio_score: float = 40.0
    execute_score: float = 85.0
    execute_risk_score: float = 70.0
    execute_strategy_score: float = 75.0
    execute_technical_score: float = 75.0
    execute_portfolio_score: float = 70.0
    execute_confidence: float = 0.80
    execute_coverage: float = 0.80
    watch_min_score: float = 70.0
    watch_max_score: float = 84.9
    slight_deficit_points: float = 5.0


@dataclass(frozen=True)
class DecisionResult:
    """Decision engine output model."""

    decision_score: float
    decision: str
    decision_quality: str
    recommendation_stability: str
    confidence: float
    coverage: float
    reasons_for: list[str] = field(default_factory=list)
    reasons_against: list[str] = field(default_factory=list)
    decision_explanation: dict[str, Any] = field(default_factory=dict)
    assessment_breakdown: dict[str, float] = field(default_factory=dict)


class DecisionEngine:
    """Aggregate existing assessments into Rule Book v1.0 recommendations."""

    _ASSESSMENT_WEIGHTS: dict[str, float] = {
        "technical": 30.0,
        "strategy": 30.0,
        "risk": 20.0,
        "portfolio": 20.0,
        "market": 0.0,
    }

    def __init__(self, thresholds: DecisionThresholds | None = None) -> None:
        self.thresholds = thresholds or DecisionThresholds()

    def evaluate(
        self,
        *,
        technical: AssessmentComponent | None,
        strategy: AssessmentComponent | None,
        risk: AssessmentComponent | None,
        portfolio: AssessmentComponent | None,
        market: AssessmentComponent | None = None,
    ) -> DecisionResult:
        assessments = {
            "technical": technical,
            "strategy": strategy,
            "risk": risk,
            "portfolio": portfolio,
            "market": market,
        }

        available = {
            name: component
            for name, component in assessments.items()
            if component is not None
        }

        if not available:
            decision_score = 0.0
            decision_quality = self._decision_quality(
                decision_score=decision_score,
                confidence=0.0,
                coverage=0.0,
                assessment_breakdown={},
            )
            return DecisionResult(
                decision_score=decision_score,
                decision="INSUFFICIENT_DATA",
                decision_quality=decision_quality,
                recommendation_stability=self._recommendation_stability(decision_score),
                confidence=0.0,
                coverage=0.0,
                reasons_for=[],
                reasons_against=["No assessment components were provided."],
                decision_explanation={"status": "no_assessments"},
                assessment_breakdown={},
            )

        weighted_total = 0.0
        total_weight = 0.0
        coverage_sum = 0.0
        confidence_sum = 0.0

        assessment_breakdown: dict[str, float] = {}
        coverage_values: list[float] = []
        confidence_values: list[float] = []

        for name, component in available.items():
            score = self._clamp_0_100(float(getattr(component, "score", 0.0)))
            coverage = self._clamp_0_1(float(getattr(component, "coverage", 0.0)))
            confidence = self._clamp_0_1(float(getattr(component, "confidence", 0.0)))

            coverage_values.append(coverage)
            confidence_values.append(confidence)
            assessment_breakdown[name] = round(score, 1)

            weight = self._ASSESSMENT_WEIGHTS.get(name, 0.0)
            if weight <= 0:
                continue

            weighted_total += score * weight
            total_weight += weight
            coverage_sum += coverage
            confidence_sum += confidence

        if total_weight <= 0:
            decision_score = 0.0
            decision_quality = self._decision_quality(
                decision_score=decision_score,
                confidence=0.0,
                coverage=0.0,
                assessment_breakdown=assessment_breakdown,
            )
            return DecisionResult(
                decision_score=decision_score,
                decision="INSUFFICIENT_DATA",
                decision_quality=decision_quality,
                recommendation_stability=self._recommendation_stability(decision_score),
                confidence=0.0,
                coverage=0.0,
                reasons_for=[],
                reasons_against=["No weighted assessments were available."],
                decision_explanation={"status": "no_weighted_assessments"},
                assessment_breakdown=assessment_breakdown,
            )

        decision_score = round(self._clamp_0_100(weighted_total / total_weight), 1)
        component_count = max(len(coverage_values), 1)
        coverage = self._clamp_0_1(sum(coverage_values) / component_count)
        base_confidence = self._clamp_0_1(sum(confidence_values) / component_count)
        confidence = self._clamp_0_1(base_confidence * (0.7 + 0.3 * coverage))

        decision, hard_override_reasons = self._resolve_rulebook_decision(
            decision_score=decision_score,
            confidence=confidence,
            coverage=coverage,
            assessment_breakdown=assessment_breakdown,
        )
        reasons_for, reasons_against = self._build_reasons(assessment_breakdown)
        reasons_against = hard_override_reasons + reasons_against
        decision_quality = self._decision_quality(
            decision_score=decision_score,
            confidence=confidence,
            coverage=coverage,
            assessment_breakdown=assessment_breakdown,
        )

        explanation = {
            "rulebook_version": "TradePilotAI Decision Rule Book v1.0",
            "hard_override_order": [
                "RULE_1_COVERAGE",
                "RULE_2_RISK",
                "RULE_3_STRATEGY",
                "RULE_4_PORTFOLIO",
            ],
            "hard_override_thresholds": {
                "minimum_coverage": self.thresholds.minimum_coverage,
                "reject_risk_score": self.thresholds.reject_risk_score,
                "reject_strategy_score": self.thresholds.reject_strategy_score,
                "watch_portfolio_score": self.thresholds.watch_portfolio_score,
            },
            "standard_decision_thresholds": {
                "execute_score": self.thresholds.execute_score,
                "execute_risk_score": self.thresholds.execute_risk_score,
                "execute_strategy_score": self.thresholds.execute_strategy_score,
                "execute_technical_score": self.thresholds.execute_technical_score,
                "execute_portfolio_score": self.thresholds.execute_portfolio_score,
                "execute_confidence": self.thresholds.execute_confidence,
                "execute_coverage": self.thresholds.execute_coverage,
                "watch_min_score": self.thresholds.watch_min_score,
                "watch_max_score": self.thresholds.watch_max_score,
            },
            "components_used": list(assessment_breakdown.keys()),
            "weighted_score": decision_score,
            "coverage": round(coverage, 3),
            "confidence": round(confidence, 3),
            "decision_quality": decision_quality,
            "recommendation_stability": self._recommendation_stability(decision_score),
            "agreement_score": round(self._assessment_agreement(assessment_breakdown), 3),
        }

        return DecisionResult(
            decision_score=decision_score,
            decision=decision,
            decision_quality=decision_quality,
            recommendation_stability=self._recommendation_stability(decision_score),
            confidence=round(confidence, 3),
            coverage=round(coverage, 3),
            reasons_for=reasons_for,
            reasons_against=reasons_against,
            decision_explanation=explanation,
            assessment_breakdown=assessment_breakdown,
        )

    def _resolve_rulebook_decision(
        self,
        *,
        decision_score: float,
        confidence: float,
        coverage: float,
        assessment_breakdown: dict[str, float],
    ) -> tuple[str, list[str]]:
        reasons: list[str] = []

        risk_score = assessment_breakdown.get("risk")
        strategy_score = assessment_breakdown.get("strategy")
        portfolio_score = assessment_breakdown.get("portfolio")
        technical_score = assessment_breakdown.get("technical")

        # RULE 1: Coverage hard override.
        if coverage < self.thresholds.minimum_coverage:
            return "INSUFFICIENT_DATA", ["Insufficient market evidence."]

        # RULE 2: Risk hard override.
        if risk_score is not None and risk_score < self.thresholds.reject_risk_score:
            return "REJECT", ["Risk exceeds acceptable threshold."]

        # RULE 3: Strategy hard override.
        if strategy_score is not None and strategy_score < self.thresholds.reject_strategy_score:
            return "REJECT", ["Strategy conditions not sufficiently satisfied."]

        # RULE 4: Portfolio hard override candidate.
        portfolio_watch_override = (
            portfolio_score is not None and portfolio_score < self.thresholds.watch_portfolio_score
        )
        if portfolio_watch_override:
            reasons.append("Trade conflicts with current portfolio.")

        execute_ready = all(
            [
                decision_score >= self.thresholds.execute_score,
                confidence >= self.thresholds.execute_confidence,
                coverage >= self.thresholds.execute_coverage,
                technical_score is not None and technical_score >= self.thresholds.execute_technical_score,
                strategy_score is not None and strategy_score >= self.thresholds.execute_strategy_score,
                risk_score is not None and risk_score >= self.thresholds.execute_risk_score,
                portfolio_score is not None and portfolio_score >= self.thresholds.execute_portfolio_score,
            ]
        )

        watch_range = self.thresholds.watch_min_score <= decision_score <= self.thresholds.watch_max_score
        one_slight_deficit = self._has_single_slight_execute_deficit(
            decision_score=decision_score,
            confidence=confidence,
            coverage=coverage,
            technical_score=technical_score,
            strategy_score=strategy_score,
            risk_score=risk_score,
            portfolio_score=portfolio_score,
        )

        # Hard portfolio override has precedence over weighted reject outcomes.
        if portfolio_watch_override:
            return "WATCH", reasons

        if execute_ready:
            return "EXECUTE", reasons
        if watch_range or one_slight_deficit:
            return "WATCH", reasons
        return "REJECT", reasons

    def _has_single_slight_execute_deficit(
        self,
        *,
        decision_score: float,
        confidence: float,
        coverage: float,
        technical_score: float | None,
        strategy_score: float | None,
        risk_score: float | None,
        portfolio_score: float | None,
    ) -> bool:
        if decision_score < self.thresholds.execute_score:
            return False

        if confidence < self.thresholds.execute_confidence or coverage < self.thresholds.execute_coverage:
            return False

        required = {
            "technical": (technical_score, self.thresholds.execute_technical_score),
            "strategy": (strategy_score, self.thresholds.execute_strategy_score),
            "risk": (risk_score, self.thresholds.execute_risk_score),
            "portfolio": (portfolio_score, self.thresholds.execute_portfolio_score),
        }

        deficits = 0
        for score, threshold in required.values():
            if score is None:
                return False
            if score >= threshold:
                continue
            if score >= threshold - self.thresholds.slight_deficit_points:
                deficits += 1
            else:
                return False

        return deficits == 1

    def _decision_quality(
        self,
        *,
        decision_score: float,
        confidence: float,
        coverage: float,
        assessment_breakdown: dict[str, float],
    ) -> str:
        agreement = self._assessment_agreement(assessment_breakdown)
        quality_index = (
            (decision_score / 100.0) * 0.45
            + confidence * 0.25
            + coverage * 0.20
            + agreement * 0.10
        )

        if quality_index >= 0.90:
            return "★★★★★ Excellent"
        if quality_index >= 0.78:
            return "★★★★☆ Strong"
        if quality_index >= 0.64:
            return "★★★☆☆ Moderate"
        if quality_index >= 0.50:
            return "★★☆☆☆ Weak"
        return "★☆☆☆☆ Poor"

    def _assessment_agreement(self, assessment_breakdown: dict[str, float]) -> float:
        values = [score for score in assessment_breakdown.values()]
        if len(values) <= 1:
            return 1.0

        spread = max(values) - min(values)
        return self._clamp_0_1(1.0 - (spread / 60.0))

    def _recommendation_stability(self, decision_score: float) -> str:
        if decision_score >= 90.0:
            return "HIGH"
        if decision_score >= 75.0:
            return "MEDIUM"
        return "LOW"

    def _build_reasons(self, assessment_breakdown: dict[str, float]) -> tuple[list[str], list[str]]:
        reasons_for: list[str] = []
        reasons_against: list[str] = []

        for name, score in assessment_breakdown.items():
            if score >= 70.0:
                reasons_for.append(f"{name.title()} assessment is supportive at {score:.1f}.")
            elif score <= 45.0:
                reasons_against.append(f"{name.title()} assessment is weak at {score:.1f}.")

        if not reasons_for:
            reasons_for.append("No strongly supportive assessments identified.")
        if not reasons_against:
            reasons_against.append("No critical assessment weakness identified.")

        return reasons_for, reasons_against

    def _clamp_0_100(self, value: float) -> float:
        if value < 0.0:
            return 0.0
        if value > 100.0:
            return 100.0
        return value

    def _clamp_0_1(self, value: float) -> float:
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value
