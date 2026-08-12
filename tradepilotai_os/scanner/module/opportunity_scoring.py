"""Opportunity scoring framework for scanner result ranking."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from .decision_engine import DecisionEngine
from .decision_engine import DecisionResult


@dataclass(frozen=True)
class OpportunityScoreWeights:
    """Configurable weighting for overall opportunity score aggregation."""

    technical: float = 40.0
    strategy: float = 20.0
    risk: float = 15.0
    portfolio: float = 15.0
    market: float = 10.0


DEFAULT_OPPORTUNITY_SCORE_WEIGHTS = OpportunityScoreWeights()


@dataclass(frozen=True)
class ScoreComponent:
    """Explainable score component with confidence and input coverage metadata."""

    score: float
    confidence: float
    coverage: float
    explanation: dict[str, float]

    def to_payload(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "confidence": self.confidence,
            "coverage": self.coverage,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OpportunityScore:
    """Structured score output for a qualifying scanner opportunity."""

    overall_score: float
    technical_score: float
    strategy_score: float
    risk_score: float
    portfolio_score: float
    market_score: float
    ranking_reason: str
    technical: ScoreComponent | None = None
    strategy: ScoreComponent | None = None
    risk: ScoreComponent | None = None
    portfolio: ScoreComponent | None = None
    market: ScoreComponent | None = None
    decision_result: DecisionResult | None = None

    @property
    def score_breakdown(self) -> dict[str, float]:
        return {
            "technical": self.technical_score,
            "strategy": self.strategy_score,
            "risk": self.risk_score,
            "portfolio": self.portfolio_score,
            "market": self.market_score,
        }

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "overall_score": self.overall_score,
            "technical_score": self.technical_score,
            "strategy_score": self.strategy_score,
            "risk_score": self.risk_score,
            "portfolio_score": self.portfolio_score,
            "market_score": self.market_score,
            "score_breakdown": self.score_breakdown,
            "ranking_reason": self.ranking_reason,
        }

        if self.technical is not None:
            payload["technical"] = self.technical.to_payload()
        if self.strategy is not None:
            payload["strategy"] = self.strategy.to_payload()
        if self.risk is not None:
            payload["risk"] = self.risk.to_payload()
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio.to_payload()
        if self.market is not None:
            payload["market"] = self.market.to_payload()
        if self.decision_result is not None:
            payload["decision_result"] = self.decision_result.to_payload()

        return payload


class OpportunityScoringEngine:
    """Framework-only scorer with placeholder component values."""

    _TECHNICAL_FACTOR_WEIGHTS: dict[str, float] = {
        "trend": 30.0,
        "rsi": 25.0,
        "momentum": 20.0,
        "signal": 15.0,
        "confidence": 10.0,
    }

    _STRATEGY_FACTOR_WEIGHTS: dict[str, float] = {
        "rule_compliance": 40.0,
        "signal_confidence": 25.0,
        "trigger_quality": 20.0,
        "signal_freshness": 15.0,
    }

    _RISK_FACTOR_WEIGHTS: dict[str, float] = {
        "reward_risk": 35.0,
        "position_risk": 25.0,
        "portfolio_exposure": 20.0,
        "stop_quality": 10.0,
        "volatility": 10.0,
    }

    _PORTFOLIO_FACTOR_WEIGHTS: dict[str, float] = {
        "diversification": 30.0,
        "sector_exposure": 25.0,
        "cash_available": 20.0,
        "position_size": 15.0,
        "portfolio_capacity": 10.0,
    }

    _MARKET_FACTOR_WEIGHTS: dict[str, float] = {
        "market_regime": 40.0,
        "trend_alignment": 30.0,
        "volatility_environment": 20.0,
        "market_breadth": 10.0,
    }

    def __init__(self, weights: OpportunityScoreWeights | None = None) -> None:
        self.weights = weights or DEFAULT_OPPORTUNITY_SCORE_WEIGHTS

    def evaluate(
        self,
        *,
        symbol: str,
        signal: str,
        confidence: int,
        volatility: float | None,
        raw_signal: Any,
        base_reason: str,
    ) -> OpportunityScore:
        technical_component = self._technical_score(symbol=symbol, signal=signal, raw_signal=raw_signal)
        strategy_component = self._strategy_score(symbol=symbol, signal=signal, raw_signal=raw_signal)
        risk_component = self._risk_score(symbol=symbol, confidence=confidence, volatility=volatility, raw_signal=raw_signal)
        portfolio_component = self._portfolio_fit_score(symbol=symbol, signal=signal, raw_signal=raw_signal)
        technical = technical_component.score
        strategy = strategy_component.score
        risk = risk_component.score
        portfolio = portfolio_component.score
        market_component = self._market_assessment_score(symbol=symbol, signal=signal, raw_signal=raw_signal)
        market = market_component.score

        decision_result = DecisionEngine().evaluate(
            technical=technical_component,
            strategy=strategy_component,
            risk=risk_component,
            portfolio=portfolio_component,
            market=market_component,
        )

        overall = self.aggregate_scores(
            technical_score=technical,
            strategy_score=strategy,
            risk_score=risk,
            portfolio_score=portfolio,
            market_score=market,
        )

        ranking_reason = (
            "Placeholder scoring framework active. "
            f"Base signal context: {base_reason or 'Strategy signal generated'}"
        )

        return OpportunityScore(
            overall_score=overall,
            technical_score=technical,
            strategy_score=strategy,
            risk_score=risk,
            portfolio_score=portfolio,
            market_score=market,
            ranking_reason=ranking_reason,
            technical=technical_component,
            strategy=strategy_component,
            risk=risk_component,
            portfolio=portfolio_component,
            market=market_component,
            decision_result=decision_result,
        )

    def aggregate_scores(
        self,
        *,
        technical_score: float,
        strategy_score: float,
        risk_score: float,
        portfolio_score: float,
        market_score: float,
    ) -> float:
        weights = self.weights
        total_weight = weights.technical + weights.strategy + weights.risk + weights.portfolio + weights.market
        if total_weight <= 0:
            return 0.0

        weighted_total = (
            technical_score * weights.technical
            + strategy_score * weights.strategy
            + risk_score * weights.risk
            + portfolio_score * weights.portfolio
            + market_score * weights.market
        )
        return round(weighted_total / total_weight, 2)

    def _technical_score(self, *, symbol: str, signal: str, raw_signal: Any) -> ScoreComponent:
        _ = symbol

        values = self._signal_values(raw_signal)
        if not values:
            return ScoreComponent(score=50.0, confidence=0.0, coverage=0.0, explanation={})

        has_explicit_trend = values.get("trend") is not None
        has_explicit_momentum = values.get("momentum") is not None

        trend_factor = self._trend_quality(signal=signal, values=values)
        rsi_factor = self._rsi_quality(signal=signal, values=values)
        momentum_factor = self._momentum_quality(signal=signal, values=values)
        signal_factor = self._signal_strength(signal=signal)
        confidence_factor = self._confidence_quality(values=values)

        weighted_score = 0.0
        available_weight = 0.0
        total_weight = sum(self._TECHNICAL_FACTOR_WEIGHTS.values())

        for factor_name, factor_value in {
            "trend": trend_factor,
            "rsi": rsi_factor,
            "momentum": momentum_factor,
            "signal": signal_factor,
            "confidence": confidence_factor,
        }.items():
            weight = self._TECHNICAL_FACTOR_WEIGHTS[factor_name]
            if factor_value is None:
                continue
            weighted_score += self._clamp_0_100(factor_value) * weight
            available_weight += weight

        if available_weight <= 0:
            return ScoreComponent(score=0.0, confidence=0.0, coverage=0.0, explanation={})

        base_score = weighted_score / available_weight

        # Missing technical inputs reduce conviction while preserving scoring continuity.
        coverage_ratio = available_weight / total_weight
        coverage_adjustment = 0.65 + 0.35 * coverage_ratio
        adjusted_score = base_score * coverage_adjustment

        if not has_explicit_trend and not has_explicit_momentum:
            adjusted_score *= 0.663

        final_score = round(self._clamp_0_100(adjusted_score), 1)
        coverage = available_weight / total_weight if total_weight > 0 else 0.0
        confidence = self._clamp_0_1(0.35 + 0.65 * coverage)
        explanation = {
            "trend_quality": round(self._weighted_contribution(trend_factor, self._TECHNICAL_FACTOR_WEIGHTS["trend"]), 2),
            "rsi_quality": round(self._weighted_contribution(rsi_factor, self._TECHNICAL_FACTOR_WEIGHTS["rsi"]), 2),
            "momentum": round(self._weighted_contribution(momentum_factor, self._TECHNICAL_FACTOR_WEIGHTS["momentum"]), 2),
            "signal_strength": round(self._weighted_contribution(signal_factor, self._TECHNICAL_FACTOR_WEIGHTS["signal"]), 2),
            "technical_confidence": round(self._weighted_contribution(confidence_factor, self._TECHNICAL_FACTOR_WEIGHTS["confidence"]), 2),
        }

        return ScoreComponent(
            score=final_score,
            confidence=round(confidence, 3),
            coverage=round(coverage, 3),
            explanation=explanation,
        )

    def _signal_values(self, raw_signal: Any) -> dict[str, Any]:
        if raw_signal is None:
            return {}
        if isinstance(raw_signal, dict):
            return dict(raw_signal)
        if hasattr(raw_signal, "__dict__"):
            return dict(vars(raw_signal))
        return {}

    def _trend_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        trend_value = values.get("trend")
        ema12 = self._as_float(values.get("ema12"))
        ema26 = self._as_float(values.get("ema26"))
        price = self._as_float(values.get("price"))

        signal_up = str(signal or "HOLD").upper()
        target_bullish = signal_up == "BUY"
        target_bearish = signal_up == "SELL"

        score_parts: list[float] = []

        if trend_value is not None:
            trend_text = str(trend_value).strip().lower()
            if target_bullish:
                score_parts.append(100.0 if trend_text == "bullish" else 35.0 if trend_text == "bearish" else 60.0)
            elif target_bearish:
                score_parts.append(100.0 if trend_text == "bearish" else 35.0 if trend_text == "bullish" else 60.0)
            else:
                score_parts.append(70.0 if trend_text == "neutral" else 60.0)

        if ema12 is not None and ema26 is not None:
            if math.isclose(ema12, ema26, rel_tol=1e-9, abs_tol=1e-9):
                ema_alignment = 60.0
            elif target_bullish:
                ema_alignment = 95.0 if ema12 > ema26 else 30.0
            elif target_bearish:
                ema_alignment = 95.0 if ema12 < ema26 else 30.0
            else:
                ema_alignment = 70.0
            score_parts.append(ema_alignment)

            if price is not None:
                ema_mid = (ema12 + ema26) / 2.0
                if target_bullish:
                    score_parts.append(85.0 if price >= ema_mid else 45.0)
                elif target_bearish:
                    score_parts.append(85.0 if price <= ema_mid else 45.0)
                else:
                    score_parts.append(65.0)

        if not score_parts:
            return None
        return sum(score_parts) / len(score_parts)

    def _rsi_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        rsi = self._as_float(values.get("rsi"))
        if rsi is None:
            return None

        signal_up = str(signal or "HOLD").upper()

        if signal_up == "BUY":
            # Favor supportive bullish momentum while penalizing overbought/weak readings.
            if rsi < 35:
                return 30.0
            if rsi <= 60:
                return 95.0
            if rsi <= 70:
                return 75.0
            return 40.0

        if signal_up == "SELL":
            if rsi > 65:
                return 30.0
            if rsi >= 40:
                return 95.0
            if rsi >= 30:
                return 75.0
            return 40.0

        # HOLD/neutral quality prefers balanced RSI.
        distance = abs(rsi - 50.0)
        return self._clamp_0_100(100.0 - distance * 2.2)

    def _momentum_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        momentum = values.get("momentum")
        signal_up = str(signal or "HOLD").upper()

        if momentum is not None:
            if isinstance(momentum, (int, float)):
                momentum_value = float(momentum)
                if -1.0 <= momentum_value <= 1.0:
                    normalized = (momentum_value + 1.0) * 50.0
                elif 0.0 <= momentum_value <= 100.0:
                    normalized = momentum_value
                else:
                    normalized = 50.0

                if signal_up == "SELL":
                    normalized = 100.0 - normalized
                return self._clamp_0_100(normalized)

            momentum_text = str(momentum).strip().lower()
            if signal_up == "BUY":
                if momentum_text in {"strong", "bullish", "up", "positive"}:
                    return 90.0
                if momentum_text in {"weak", "bearish", "down", "negative"}:
                    return 30.0
                return 55.0
            if signal_up == "SELL":
                if momentum_text in {"strong", "bearish", "down", "negative"}:
                    return 90.0
                if momentum_text in {"weak", "bullish", "up", "positive"}:
                    return 30.0
                return 55.0
            return 55.0

        # If momentum is absent, use existing EMA spread as scanner-derived momentum proxy.
        ema12 = self._as_float(values.get("ema12"))
        ema26 = self._as_float(values.get("ema26"))
        if ema12 is None or ema26 is None or math.isclose(ema26, 0.0, abs_tol=1e-12):
            return None

        spread_pct = ((ema12 - ema26) / abs(ema26)) * 100.0
        normalized = self._clamp_0_100(50.0 + spread_pct * 8.0)
        if signal_up == "SELL":
            normalized = 100.0 - normalized
        return self._clamp_0_100(normalized)

    def _signal_strength(self, *, signal: str) -> float:
        signal_up = str(signal or "HOLD").upper()
        if signal_up in {"BUY", "SELL"}:
            return 85.0
        if signal_up in {"WATCH", "HOLD"}:
            return 45.0
        return 50.0

    def _confidence_quality(self, *, values: dict[str, Any]) -> float | None:
        confidence = self._as_float(values.get("confidence"))
        if confidence is None:
            return None
        return self._clamp_0_100(confidence)

    def _as_float(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

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

    def _weighted_contribution(self, factor_value: float | None, weight: float) -> float:
        if factor_value is None:
            return 0.0
        return self._clamp_0_100(factor_value) * (weight / 100.0)

    def _strategy_score(self, *, symbol: str, signal: str, raw_signal: Any) -> ScoreComponent:
        _ = symbol

        values = self._signal_values(raw_signal)
        if not values:
            return ScoreComponent(score=50.0, confidence=0.0, coverage=0.0, explanation={})

        has_rule_fields = any(key in values for key in ("rule_results", "rules", "rule_checks", "strategy_rules"))
        has_trigger_fields = any(key in values for key in ("trigger_status", "trigger", "triggered", "entry_trigger"))
        has_freshness_fields = any(key in values for key in ("signal_freshness", "freshness", "signal_age", "age_minutes", "minutes_since_signal"))
        has_strategy_identity = any(
            str(values.get(key) or "").strip()
            for key in ("strategy_name", "strategy", "active_strategy")
        )

        if not (has_rule_fields or has_trigger_fields or has_freshness_fields or has_strategy_identity):
            return ScoreComponent(score=50.0, confidence=0.0, coverage=0.0, explanation={})

        rule_factor = self._strategy_rule_compliance(values=values)
        confidence_factor = self._strategy_signal_confidence(values=values)
        trigger_factor = self._strategy_trigger_quality(signal=signal, values=values)
        freshness_factor = self._strategy_signal_freshness(values=values)

        weighted_score = 0.0
        available_weight = 0.0

        for factor_name, factor_value in {
            "rule_compliance": rule_factor,
            "signal_confidence": confidence_factor,
            "trigger_quality": trigger_factor,
            "signal_freshness": freshness_factor,
        }.items():
            weight = self._STRATEGY_FACTOR_WEIGHTS[factor_name]
            if factor_value is None:
                continue
            weighted_score += self._clamp_0_100(factor_value) * weight
            available_weight += weight

        if available_weight <= 0:
            return ScoreComponent(score=50.0, confidence=0.0, coverage=0.0, explanation={})

        base_score = weighted_score / available_weight

        total_weight = sum(self._STRATEGY_FACTOR_WEIGHTS.values())
        coverage_ratio = available_weight / total_weight
        coverage_adjustment = 0.65 + 0.35 * coverage_ratio
        adjusted_score = base_score * coverage_adjustment

        if rule_factor is None and trigger_factor is None and freshness_factor is None:
            adjusted_score = (adjusted_score + 50.0) / 2.0

        final_score = round(self._clamp_0_100(adjusted_score), 1)
        total_weight = sum(self._STRATEGY_FACTOR_WEIGHTS.values())
        coverage = available_weight / total_weight if total_weight > 0 else 0.0
        confidence = self._clamp_0_1(0.3 + 0.7 * coverage)
        explanation = {
            "rule_compliance": round(self._weighted_contribution(rule_factor, self._STRATEGY_FACTOR_WEIGHTS["rule_compliance"]), 2),
            "signal_confidence": round(self._weighted_contribution(confidence_factor, self._STRATEGY_FACTOR_WEIGHTS["signal_confidence"]), 2),
            "trigger_quality": round(self._weighted_contribution(trigger_factor, self._STRATEGY_FACTOR_WEIGHTS["trigger_quality"]), 2),
            "signal_freshness": round(self._weighted_contribution(freshness_factor, self._STRATEGY_FACTOR_WEIGHTS["signal_freshness"]), 2),
        }

        return ScoreComponent(
            score=final_score,
            confidence=round(confidence, 3),
            coverage=round(coverage, 3),
            explanation=explanation,
        )

    def _strategy_rule_compliance(self, *, values: dict[str, Any]) -> float | None:
        for key in ("rule_results", "rules", "rule_checks", "strategy_rules"):
            if key not in values:
                continue

            rule_data = values.get(key)
            ratio = self._truthy_ratio(rule_data)
            if ratio is None:
                continue
            return self._clamp_0_100(ratio * 100.0)

        return None

    def _strategy_signal_confidence(self, *, values: dict[str, Any]) -> float | None:
        for key in ("confidence", "signal_confidence", "strategy_confidence"):
            confidence = self._as_float(values.get(key))
            if confidence is None:
                continue

            if 0.0 <= confidence <= 1.0:
                confidence *= 100.0
            return self._clamp_0_100(confidence)

        return None

    def _strategy_trigger_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        trigger_value = None
        for key in ("trigger_status", "trigger", "triggered", "entry_trigger"):
            if key in values:
                trigger_value = values.get(key)
                break

        strategy_name = ""
        for key in ("strategy_name", "strategy", "active_strategy"):
            value = values.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                strategy_name = text
                break

        signal_up = str(signal or values.get("signal") or "HOLD").upper()
        signal_quality = 55.0
        if signal_up in {"BUY", "SELL"}:
            signal_quality = 80.0
        elif signal_up in {"HOLD", "WATCH"}:
            signal_quality = 45.0

        trigger_quality = None
        if trigger_value is not None:
            if isinstance(trigger_value, bool):
                trigger_quality = 100.0 if trigger_value else 25.0
            elif isinstance(trigger_value, (int, float)):
                numeric = float(trigger_value)
                if 0.0 <= numeric <= 1.0:
                    numeric *= 100.0
                trigger_quality = self._clamp_0_100(numeric)
            else:
                trigger_text = str(trigger_value).strip().lower()
                if trigger_text in {"triggered", "active", "confirmed", "true", "yes", "ready"}:
                    trigger_quality = 95.0
                elif trigger_text in {"partial", "pending", "forming"}:
                    trigger_quality = 60.0
                elif trigger_text in {"failed", "inactive", "false", "no", "blocked"}:
                    trigger_quality = 25.0
                else:
                    trigger_quality = 50.0

        strategy_bonus = 5.0 if strategy_name else 0.0

        if trigger_quality is None and strategy_bonus <= 0.0 and signal_up == "HOLD":
            return None

        if trigger_quality is None:
            return self._clamp_0_100(signal_quality + strategy_bonus)

        return self._clamp_0_100(trigger_quality * 0.75 + signal_quality * 0.25 + strategy_bonus)

    def _strategy_signal_freshness(self, *, values: dict[str, Any]) -> float | None:
        for key in ("signal_freshness", "freshness", "signal_age", "age_minutes", "minutes_since_signal"):
            if key not in values:
                continue

            freshness = values.get(key)

            if isinstance(freshness, bool):
                return 90.0 if freshness else 35.0

            numeric = self._as_float(freshness)
            if numeric is not None:
                # Treat numeric values as age in minutes: fresher signals score higher.
                if numeric <= 0:
                    return 95.0
                if numeric <= 15:
                    return 90.0
                if numeric <= 60:
                    return 75.0
                if numeric <= 240:
                    return 55.0
                if numeric <= 1440:
                    return 40.0
                return 25.0

            freshness_text = str(freshness).strip().lower()
            if freshness_text in {"fresh", "new", "recent", "current"}:
                return 90.0
            if freshness_text in {"stale", "old", "aged", "expired"}:
                return 25.0
            if freshness_text in {"moderate", "mid", "normal"}:
                return 60.0
            return 50.0

        return None

    def _truthy_ratio(self, values: Any) -> float | None:
        if values is None:
            return None

        if isinstance(values, dict):
            values = list(values.values())
        elif not isinstance(values, (list, tuple, set)):
            values = [values]

        normalized = list(values)
        if not normalized:
            return None

        passed = 0
        seen = 0
        for item in normalized:
            truthy = self._as_truthy(item)
            if truthy is None:
                continue
            seen += 1
            if truthy:
                passed += 1

        if seen == 0:
            return None
        return passed / seen

    def _as_truthy(self, value: Any) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value > 0

        text = str(value).strip().lower()
        if not text:
            return None
        if text in {"true", "pass", "passed", "ok", "yes", "y", "active", "triggered", "confirmed"}:
            return True
        if text in {"false", "fail", "failed", "no", "n", "inactive", "blocked", "rejected"}:
            return False
        return None

    def _risk_score(
        self,
        *,
        symbol: str,
        confidence: int,
        volatility: float | None,
        raw_signal: Any,
    ) -> ScoreComponent:
        _ = (symbol, confidence)

        values = self._signal_values(raw_signal)
        reward_risk_factor = self._risk_reward_risk_quality(values=values)
        position_risk_factor = self._risk_position_risk_quality(values=values)
        portfolio_exposure_factor = self._risk_portfolio_exposure_quality(values=values)
        stop_quality_factor = self._risk_stop_placement_quality(values=values)
        volatility_factor = self._risk_volatility_quality(values=values, volatility=volatility)

        weighted_score = 0.0
        available_weight = 0.0

        for factor_name, factor_value in {
            "reward_risk": reward_risk_factor,
            "position_risk": position_risk_factor,
            "portfolio_exposure": portfolio_exposure_factor,
            "stop_quality": stop_quality_factor,
            "volatility": volatility_factor,
        }.items():
            weight = self._RISK_FACTOR_WEIGHTS[factor_name]
            if factor_value is None:
                continue
            weighted_score += self._clamp_0_100(factor_value) * weight
            available_weight += weight

        total_weight = sum(self._RISK_FACTOR_WEIGHTS.values())
        coverage = available_weight / total_weight if total_weight > 0 else 0.0

        explanation = {
            "reward_risk": round(self._weighted_contribution(reward_risk_factor, self._RISK_FACTOR_WEIGHTS["reward_risk"]), 2),
            "position_risk": round(self._weighted_contribution(position_risk_factor, self._RISK_FACTOR_WEIGHTS["position_risk"]), 2),
            "portfolio_exposure": round(self._weighted_contribution(portfolio_exposure_factor, self._RISK_FACTOR_WEIGHTS["portfolio_exposure"]), 2),
            "stop_quality": round(self._weighted_contribution(stop_quality_factor, self._RISK_FACTOR_WEIGHTS["stop_quality"]), 2),
            "volatility": round(self._weighted_contribution(volatility_factor, self._RISK_FACTOR_WEIGHTS["volatility"]), 2),
        }

        # Keep scanner behavior stable: sparse evidence remains neutral.
        if available_weight < 25.0:
            confidence_score = self._clamp_0_1(0.2 + 0.6 * coverage)
            return ScoreComponent(
                score=50.0,
                confidence=round(confidence_score, 3),
                coverage=round(coverage, 3),
                explanation=explanation,
            )

        base_score = weighted_score / available_weight
        coverage_adjustment = 0.7 + 0.3 * coverage
        adjusted_score = base_score * coverage_adjustment
        final_score = round(self._clamp_0_100(adjusted_score), 1)
        confidence_score = self._clamp_0_1(0.3 + 0.7 * coverage)

        return ScoreComponent(
            score=final_score,
            confidence=round(confidence_score, 3),
            coverage=round(coverage, 3),
            explanation=explanation,
        )

    def _risk_reward_risk_quality(self, *, values: dict[str, Any]) -> float | None:
        ratio_keys = ("reward_risk", "reward_risk_ratio", "rr_ratio", "rr")
        ratio_value = None
        for key in ratio_keys:
            parsed = self._parse_ratio(values.get(key))
            if parsed is not None:
                ratio_value = parsed
                break

        if ratio_value is None:
            return None

        if ratio_value >= 3.0:
            return 95.0
        if ratio_value >= 2.0:
            return 85.0
        if ratio_value >= 1.5:
            return 75.0
        if ratio_value >= 1.0:
            return 60.0
        if ratio_value >= 0.7:
            return 40.0
        return 20.0

    def _risk_position_risk_quality(self, *, values: dict[str, Any]) -> float | None:
        risk_pct = self._as_float(
            values.get("position_risk_pct")
            or values.get("position_risk")
            or values.get("risk_percent")
        )
        if risk_pct is not None:
            if risk_pct <= 0.5:
                return 95.0
            if risk_pct <= 1.0:
                return 85.0
            if risk_pct <= 2.0:
                return 70.0
            if risk_pct <= 3.0:
                return 50.0
            if risk_pct <= 5.0:
                return 30.0
            return 15.0

        status = values.get("risk_status") or values.get("risk")
        if status is None:
            return None
        status_text = str(status).strip().lower()
        if status_text == "low":
            return 85.0
        if status_text == "medium":
            return 60.0
        if status_text == "high":
            return 30.0
        return 50.0

    def _risk_portfolio_exposure_quality(self, *, values: dict[str, Any]) -> float | None:
        exposure = self._as_float(
            values.get("portfolio_exposure")
            or values.get("exposure")
            or values.get("exposure_percent")
        )
        if exposure is None:
            return None

        if exposure <= 20.0:
            return 90.0
        if exposure <= 40.0:
            return 75.0
        if exposure <= 60.0:
            return 55.0
        if exposure <= 80.0:
            return 35.0
        return 20.0

    def _risk_stop_placement_quality(self, *, values: dict[str, Any]) -> float | None:
        stop_distance = self._as_float(values.get("stop_distance") or values.get("stop_loss_distance"))
        target_distance = self._as_float(values.get("target_distance") or values.get("take_profit_distance"))

        if stop_distance is None:
            return None

        if stop_distance <= 0:
            return 10.0

        stop_score = 50.0
        if stop_distance < 0.25:
            stop_score = 35.0
        elif stop_distance <= 0.5:
            stop_score = 60.0
        elif stop_distance <= 3.0:
            stop_score = 85.0
        elif stop_distance <= 5.0:
            stop_score = 70.0
        else:
            stop_score = 40.0

        if target_distance is None or target_distance <= 0:
            return stop_score

        distance_ratio = target_distance / stop_distance
        if distance_ratio >= 2.0:
            ratio_score = 90.0
        elif distance_ratio >= 1.5:
            ratio_score = 80.0
        elif distance_ratio >= 1.0:
            ratio_score = 65.0
        elif distance_ratio >= 0.7:
            ratio_score = 45.0
        else:
            ratio_score = 25.0

        return self._clamp_0_100((stop_score * 0.6) + (ratio_score * 0.4))

    def _risk_volatility_quality(self, *, values: dict[str, Any], volatility: float | None) -> float | None:
        raw_vol = self._as_float(values.get("volatility"))
        if raw_vol is None:
            raw_vol = self._as_float(volatility)
        if raw_vol is None:
            return None

        vol = abs(raw_vol)
        if vol <= 0.01:
            return 90.0
        if vol <= 0.02:
            return 80.0
        if vol <= 0.03:
            return 65.0
        if vol <= 0.05:
            return 45.0
        return 25.0

    def _parse_ratio(self, value: Any) -> float | None:
        numeric = self._as_float(value)
        if numeric is not None:
            return numeric

        if value is None:
            return None

        text = str(value).strip().lower()
        if not text:
            return None

        if ":" in text:
            left, right = text.split(":", 1)
            left_num = self._as_float(left.strip())
            right_num = self._as_float(right.strip())
            if left_num is None or right_num is None or left_num == 0:
                return None
            return right_num / left_num

        return None

    def _portfolio_fit_score(self, *, symbol: str, signal: str, raw_signal: Any) -> ScoreComponent:
        _ = (symbol, signal)

        values = self._signal_values(raw_signal)
        diversification_factor = self._portfolio_diversification_quality(values=values)
        sector_factor = self._portfolio_sector_exposure_quality(values=values)
        cash_factor = self._portfolio_cash_availability_quality(values=values)
        position_size_factor = self._portfolio_position_size_quality(values=values)
        capacity_factor = self._portfolio_capacity_quality(values=values)

        weighted_score = 0.0
        available_weight = 0.0

        for factor_name, factor_value in {
            "diversification": diversification_factor,
            "sector_exposure": sector_factor,
            "cash_available": cash_factor,
            "position_size": position_size_factor,
            "portfolio_capacity": capacity_factor,
        }.items():
            weight = self._PORTFOLIO_FACTOR_WEIGHTS[factor_name]
            if factor_value is None:
                continue
            weighted_score += self._clamp_0_100(factor_value) * weight
            available_weight += weight

        total_weight = sum(self._PORTFOLIO_FACTOR_WEIGHTS.values())
        coverage = available_weight / total_weight if total_weight > 0 else 0.0

        explanation = {
            "diversification": round(self._weighted_contribution(diversification_factor, self._PORTFOLIO_FACTOR_WEIGHTS["diversification"]), 2),
            "sector_exposure": round(self._weighted_contribution(sector_factor, self._PORTFOLIO_FACTOR_WEIGHTS["sector_exposure"]), 2),
            "cash_available": round(self._weighted_contribution(cash_factor, self._PORTFOLIO_FACTOR_WEIGHTS["cash_available"]), 2),
            "position_size": round(self._weighted_contribution(position_size_factor, self._PORTFOLIO_FACTOR_WEIGHTS["position_size"]), 2),
            "portfolio_capacity": round(self._weighted_contribution(capacity_factor, self._PORTFOLIO_FACTOR_WEIGHTS["portfolio_capacity"]), 2),
        }

        # Keep scanner behavior stable on sparse portfolio payloads.
        if available_weight < 20.0:
            confidence_score = self._clamp_0_1(0.2 + 0.6 * coverage)
            return ScoreComponent(
                score=50.0,
                confidence=round(confidence_score, 3),
                coverage=round(coverage, 3),
                explanation=explanation,
            )

        base_score = weighted_score / available_weight
        coverage_adjustment = 0.7 + 0.3 * coverage
        final_score = round(self._clamp_0_100(base_score * coverage_adjustment), 1)
        confidence_score = self._clamp_0_1(0.3 + 0.7 * coverage)

        return ScoreComponent(
            score=final_score,
            confidence=round(confidence_score, 3),
            coverage=round(coverage, 3),
            explanation=explanation,
        )

    def _portfolio_diversification_quality(self, *, values: dict[str, Any]) -> float | None:
        holdings = values.get("existing_holdings") or values.get("holdings") or values.get("open_positions")
        symbol = values.get("symbol") or values.get("ticker")
        if holdings is None:
            return None

        if isinstance(holdings, dict):
            holding_symbols = {str(key).upper() for key in holdings.keys()}
        elif isinstance(holdings, (list, tuple, set)):
            holding_symbols = {str(item).upper() for item in holdings}
        else:
            holding_symbols = {str(holdings).upper()}

        if symbol is None:
            return 65.0

        return 30.0 if str(symbol).upper() in holding_symbols else 85.0

    def _portfolio_sector_exposure_quality(self, *, values: dict[str, Any]) -> float | None:
        sector_exposure = self._as_float(values.get("sector_exposure") or values.get("sector_allocation"))
        if sector_exposure is not None:
            if sector_exposure <= 15.0:
                return 90.0
            if sector_exposure <= 25.0:
                return 75.0
            if sector_exposure <= 35.0:
                return 55.0
            if sector_exposure <= 50.0:
                return 35.0
            return 20.0

        sector_status = values.get("sector_status") or values.get("sector_risk")
        if sector_status is None:
            return None
        status = str(sector_status).strip().lower()
        if status in {"low", "diversified", "balanced"}:
            return 80.0
        if status in {"medium", "watch"}:
            return 55.0
        if status in {"high", "concentrated"}:
            return 25.0
        return 50.0

    def _portfolio_cash_availability_quality(self, *, values: dict[str, Any]) -> float | None:
        cash = self._as_float(values.get("cash_available") or values.get("cash") or values.get("buying_power"))
        if cash is None:
            return None

        if cash <= 0:
            return 15.0
        if cash < 1000:
            return 35.0
        if cash < 5000:
            return 55.0
        if cash < 20000:
            return 75.0
        return 90.0

    def _portfolio_position_size_quality(self, *, values: dict[str, Any]) -> float | None:
        position_size = self._as_float(values.get("position_size_recommendation") or values.get("position_size"))
        max_size = self._as_float(values.get("max_position_size") or values.get("portfolio_limits_max_position") or values.get("portfolio_limit"))
        allocation = self._as_float(values.get("allocation_percent") or values.get("allocation"))

        if position_size is not None and max_size is not None and max_size > 0:
            ratio = position_size / max_size
            if ratio <= 0.25:
                return 90.0
            if ratio <= 0.5:
                return 80.0
            if ratio <= 0.75:
                return 60.0
            if ratio <= 1.0:
                return 45.0
            return 20.0

        if allocation is not None:
            if allocation <= 2.0:
                return 90.0
            if allocation <= 5.0:
                return 75.0
            if allocation <= 10.0:
                return 55.0
            if allocation <= 20.0:
                return 35.0
            return 20.0

        return None

    def _portfolio_capacity_quality(self, *, values: dict[str, Any]) -> float | None:
        exposure = self._as_float(values.get("current_portfolio_exposure") or values.get("portfolio_exposure") or values.get("exposure_percent"))
        open_positions = self._as_float(values.get("open_positions_count") or values.get("open_positions"))
        max_positions = self._as_float(values.get("max_positions") or values.get("portfolio_limits_max_positions"))

        score_parts: list[float] = []

        if exposure is not None:
            if exposure <= 40.0:
                score_parts.append(90.0)
            elif exposure <= 60.0:
                score_parts.append(70.0)
            elif exposure <= 80.0:
                score_parts.append(45.0)
            else:
                score_parts.append(20.0)

        if open_positions is not None and max_positions is not None and max_positions > 0:
            ratio = open_positions / max_positions
            if ratio <= 0.5:
                score_parts.append(90.0)
            elif ratio <= 0.75:
                score_parts.append(70.0)
            elif ratio <= 1.0:
                score_parts.append(45.0)
            else:
                score_parts.append(20.0)

        if not score_parts:
            return None
        return sum(score_parts) / len(score_parts)

    def _market_assessment_score(self, *, symbol: str, signal: str, raw_signal: Any) -> ScoreComponent:
        _ = symbol

        values = self._signal_values(raw_signal)

        market_regime_factor = self._market_regime_quality(signal=signal, values=values)
        trend_alignment_factor = self._market_trend_alignment_quality(signal=signal, values=values)
        volatility_environment_factor = self._market_volatility_environment_quality(values=values)
        market_breadth_factor = self._market_breadth_quality(signal=signal, values=values)

        weighted_score = 0.0
        available_weight = 0.0

        for factor_name, factor_value in {
            "market_regime": market_regime_factor,
            "trend_alignment": trend_alignment_factor,
            "volatility_environment": volatility_environment_factor,
            "market_breadth": market_breadth_factor,
        }.items():
            weight = self._MARKET_FACTOR_WEIGHTS[factor_name]
            if factor_value is None:
                continue
            weighted_score += self._clamp_0_100(factor_value) * weight
            available_weight += weight

        total_weight = sum(self._MARKET_FACTOR_WEIGHTS.values())
        coverage = available_weight / total_weight if total_weight > 0 else 0.0

        explanation = {
            "market_regime": round(self._weighted_contribution(market_regime_factor, self._MARKET_FACTOR_WEIGHTS["market_regime"]), 2),
            "trend_alignment": round(self._weighted_contribution(trend_alignment_factor, self._MARKET_FACTOR_WEIGHTS["trend_alignment"]), 2),
            "volatility_environment": round(self._weighted_contribution(volatility_environment_factor, self._MARKET_FACTOR_WEIGHTS["volatility_environment"]), 2),
            "market_breadth": round(self._weighted_contribution(market_breadth_factor, self._MARKET_FACTOR_WEIGHTS["market_breadth"]), 2),
        }

        if available_weight <= 0:
            return ScoreComponent(score=50.0, confidence=0.0, coverage=0.0, explanation=explanation)

        base_score = weighted_score / available_weight
        score = round(self._clamp_0_100(base_score), 1)

        payload_confidence = self._market_payload_confidence(values=values)
        confidence = self._clamp_0_1(0.25 + 0.75 * coverage)
        if payload_confidence is not None:
            confidence = self._clamp_0_1(confidence * 0.6 + payload_confidence * 0.4)

        # Sparse market evidence should stay neutral to preserve scanner behavior.
        if available_weight < 20.0:
            return ScoreComponent(
                score=50.0,
                confidence=round(confidence, 3),
                coverage=round(coverage, 3),
                explanation=explanation,
            )

        return ScoreComponent(
            score=score,
            confidence=round(confidence, 3),
            coverage=round(coverage, 3),
            explanation=explanation,
        )

    def _market_regime_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        regime_value = self._first_market_value(
            values,
            "market_regime",
            "regime",
            "market_environment",
            "market_state",
        )
        bias = self._directional_bias(regime_value)
        if bias is None:
            return None
        return self._signal_alignment_score(signal=signal, bias=bias)

    def _market_trend_alignment_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        market_trend = self._first_market_value(
            values,
            "market_trend",
            "trend",
            "market_direction",
        )
        index_trend = self._first_market_value(
            values,
            "index_trend",
            "benchmark_trend",
            "spy_trend",
            "qqq_trend",
        )

        trend_scores: list[float] = []

        market_bias = self._directional_bias(market_trend)
        if market_bias is not None:
            trend_scores.append(self._signal_alignment_score(signal=signal, bias=market_bias))

        index_bias = self._directional_bias(index_trend)
        if index_bias is not None:
            trend_scores.append(self._signal_alignment_score(signal=signal, bias=index_bias))

        if not trend_scores:
            return None
        return sum(trend_scores) / len(trend_scores)

    def _market_volatility_environment_quality(self, *, values: dict[str, Any]) -> float | None:
        volatility_regime = self._first_market_value(
            values,
            "volatility_regime",
            "market_volatility_regime",
            "vix_regime",
            "vol_regime",
        )
        if volatility_regime is not None:
            text = str(volatility_regime).strip().lower()
            if text in {"very low", "low", "calm", "compressed", "benign"}:
                return 85.0
            if text in {"moderate", "normal", "neutral", "balanced"}:
                return 75.0
            if text in {"high", "elevated", "volatile", "risk-off"}:
                return 40.0
            if text in {"extreme", "spike", "panic"}:
                return 20.0

        market_volatility = self._as_float(
            self._first_market_value(
                values,
                "market_volatility",
                "volatility",
                "vix",
            )
        )
        if market_volatility is None:
            return None

        vol = abs(market_volatility)
        if vol <= 0.01:
            return 85.0
        if vol <= 0.02:
            return 75.0
        if vol <= 0.03:
            return 65.0
        if vol <= 0.05:
            return 45.0
        return 25.0

    def _market_breadth_quality(self, *, signal: str, values: dict[str, Any]) -> float | None:
        breadth_value = self._first_market_value(
            values,
            "market_breadth",
            "breadth",
            "breadth_trend",
            "advance_decline",
            "ad_ratio",
        )
        if breadth_value is None:
            return None

        numeric_breadth = self._as_float(breadth_value)
        if numeric_breadth is not None:
            if -1.0 <= numeric_breadth <= 1.0:
                if numeric_breadth >= 0.2:
                    return self._signal_alignment_score(signal=signal, bias=1.0)
                if numeric_breadth <= -0.2:
                    return self._signal_alignment_score(signal=signal, bias=-1.0)
                return self._signal_alignment_score(signal=signal, bias=0.0)

            if numeric_breadth >= 60.0:
                return self._signal_alignment_score(signal=signal, bias=1.0)
            if numeric_breadth <= 40.0:
                return self._signal_alignment_score(signal=signal, bias=-1.0)
            return self._signal_alignment_score(signal=signal, bias=0.0)

        bias = self._directional_bias(breadth_value)
        if bias is None:
            return None
        return self._signal_alignment_score(signal=signal, bias=bias)

    def _market_payload_confidence(self, *, values: dict[str, Any]) -> float | None:
        raw_confidence = self._first_market_value(
            values,
            "market_confidence",
            "market_quality_confidence",
            "environment_confidence",
        )
        confidence = self._as_float(raw_confidence)
        if confidence is None:
            return None

        if confidence > 1.0:
            confidence /= 100.0
        return self._clamp_0_1(confidence)

    def _first_market_value(self, values: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            if key in values and values.get(key) is not None:
                return values.get(key)

        nested_keys = (
            "market",
            "market_data",
            "market_status",
            "market_context",
            "environment",
        )
        for nested_key in nested_keys:
            nested = values.get(nested_key)
            if not isinstance(nested, dict):
                continue
            for key in keys:
                if key in nested and nested.get(key) is not None:
                    return nested.get(key)
        return None

    def _directional_bias(self, value: Any) -> float | None:
        if value is None:
            return None

        numeric = self._as_float(value)
        if numeric is not None:
            if -1.0 <= numeric <= 1.0:
                if numeric > 0.15:
                    return 1.0
                if numeric < -0.15:
                    return -1.0
                return 0.0

            if numeric >= 60.0:
                return 1.0
            if numeric <= 40.0:
                return -1.0
            return 0.0

        text = str(value).strip().lower()
        bullish = {
            "bull", "bullish", "up", "uptrend", "risk_on", "risk-on", "positive", "strong", "expansion"
        }
        bearish = {
            "bear", "bearish", "down", "downtrend", "risk_off", "risk-off", "negative", "weak", "contraction"
        }
        neutral = {"neutral", "sideways", "mixed", "range", "balanced", "flat", "choppy"}

        if text in bullish:
            return 1.0
        if text in bearish:
            return -1.0
        if text in neutral:
            return 0.0
        return None

    def _signal_alignment_score(self, *, signal: str, bias: float) -> float:
        signal_up = str(signal or "HOLD").upper()

        if signal_up == "BUY":
            if bias > 0.0:
                return 90.0
            if bias < 0.0:
                return 25.0
            return 60.0

        if signal_up == "SELL":
            if bias < 0.0:
                return 90.0
            if bias > 0.0:
                return 25.0
            return 60.0

        return 65.0 if bias == 0.0 else 55.0
