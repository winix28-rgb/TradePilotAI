"""Exit engine for paper trading positions."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict
from datetime import datetime, timezone
from math import inf
from typing import Any, Protocol

from .engine import PaperPortfolioEngine


@dataclass(slots=True)
class ExitDecision:
    should_exit: bool
    exit_reason: str
    confidence: float = 0.0
    explanation: str = ""
    exit_type: str = "STRATEGY_EXIT"


class StrategyForExit(Protocol):
    def should_exit(self, position: Any, context: dict[str, Any] | None = None) -> ExitDecision | dict[str, Any] | None:
        ...


class StrategyResolver(Protocol):
    def resolve(self, position: Any, context: dict[str, Any] | None = None) -> StrategyForExit | None:
        ...


class MappingStrategyResolver:
    """Resolve strategy instances from the runtime context mapping."""

    def resolve(self, position: Any, context: dict[str, Any] | None = None) -> StrategyForExit | None:
        if not isinstance(context, dict):
            return None
        strategies = context.get("strategies")
        if not isinstance(strategies, dict):
            return None

        strategy_id = str(getattr(position, "strategy_id", "") or "")
        strategy_name = str(getattr(position, "strategy_name", "") or "")
        strategy = strategies.get(strategy_id)
        if strategy is None and strategy_name:
            strategy = strategies.get(strategy_name)
        if strategy is None:
            return None
        return strategy



class ExitEngine:
    """Determine and execute exits while delegating state mutation to the portfolio engine."""

    SUPPORTED_EXIT_TYPES = {
        "MANUAL_EXIT",
        "STOP_LOSS",
        "TAKE_PROFIT",
        "STRATEGY_EXIT",
        "EMERGENCY_CLOSE",
        "END_OF_SESSION",
        "END_OF_TEST",
    }

    def __init__(self, portfolio_engine: PaperPortfolioEngine, strategy_resolver: StrategyResolver | None = None) -> None:
        self.portfolio_engine = portfolio_engine
        self.strategy_resolver = strategy_resolver or MappingStrategyResolver()

    def process_exits(self, strategy_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        closed: list[dict[str, Any]] = []
        for position in list(self.portfolio_engine.get_open_positions()):
            try:
                decision = self._determine_exit(position, strategy_context=strategy_context)
            except Exception as error:
                self.portfolio_engine.record_audit_event(
                    "EXIT_EVALUATION_FAILED",
                    utc_timestamp=self._utc_now(),
                    position_id=getattr(position, "position_id", ""),
                    symbol=getattr(position, "symbol", ""),
                    reason=f"Exit evaluation failed: {error}",
                )
                continue
            if decision is None:
                continue
            closed_trade = self._execute_exit(position, decision=decision)
            if closed_trade is not None:
                closed.append(asdict(closed_trade))

        if closed:
            self.portfolio_engine.record_audit_event(
                "PORTFOLIO_UPDATED",
                utc_timestamp=self._utc_now(),
                reason="Exit engine processed position exits.",
                closed_count=len(closed),
            )
        return closed

    def close_position(
        self,
        position_id: str,
        *,
        exit_price: float | None = None,
        reason: str = "MANUAL_EXIT",
        explanation: str = "",
    ) -> Any:
        position = self.portfolio_engine.get_open_position_by_id(position_id)
        if position is None:
            return None

        resolved_price = float(exit_price) if exit_price is not None else float(getattr(position, "current_price", 0.0) or 0.0)
        decision = {
            "type": "MANUAL_EXIT",
            "reason": reason if reason in self.SUPPORTED_EXIT_TYPES else "MANUAL_EXIT",
            "explanation": explanation or "Manual user-requested close.",
            "confidence": 1.0,
            "exit_price": resolved_price,
        }
        return self._execute_exit(position, decision=decision)

    def manual_exit(self, symbol: str, *, exit_price: float | None = None, reason: str = "MANUAL_EXIT", explanation: str = "") -> Any:
        position = self.portfolio_engine.get_open_position(symbol)
        if position is None:
            return None
        return self.close_position(
            position.position_id,
            exit_price=exit_price,
            reason=reason,
            explanation=explanation,
        )

    def _determine_exit(self, position: Any, strategy_context: dict[str, Any] | None = None) -> dict[str, Any] | None:
        current_price = float(getattr(position, "current_price", 0.0) or 0.0)
        stop_loss = float(getattr(position, "stop_loss", 0.0) or 0.0)
        target = float(getattr(position, "target", 0.0) or 0.0)
        direction = str(getattr(position, "direction", "BUY") or "BUY").upper()

        if direction == "SELL":
            if stop_loss > 0 and current_price >= stop_loss:
                return {
                    "type": "STOP_LOSS",
                    "reason": "STOP_LOSS",
                    "explanation": "Current market price crossed stop loss.",
                    "confidence": 1.0,
                    "exit_price": current_price,
                }
            if target > 0 and current_price <= target:
                return {
                    "type": "TAKE_PROFIT",
                    "reason": "TAKE_PROFIT",
                    "explanation": "Current market price reached target.",
                    "confidence": 1.0,
                    "exit_price": current_price,
                }
        else:
            if stop_loss > 0 and current_price <= stop_loss:
                return {
                    "type": "STOP_LOSS",
                    "reason": "STOP_LOSS",
                    "explanation": "Current market price crossed stop loss.",
                    "confidence": 1.0,
                    "exit_price": current_price,
                }
            if target > 0 and current_price >= target:
                return {
                    "type": "TAKE_PROFIT",
                    "reason": "TAKE_PROFIT",
                    "explanation": "Current market price reached target.",
                    "confidence": 1.0,
                    "exit_price": current_price,
                }

        strategy = self.strategy_resolver.resolve(position, strategy_context)
        if strategy is None:
            return None

        raw_decision = strategy.should_exit(position, strategy_context)
        decision = self._normalize_strategy_decision(raw_decision)
        if decision is None or not decision.should_exit:
            return None

        return {
            "type": decision.exit_type if decision.exit_type in self.SUPPORTED_EXIT_TYPES else "STRATEGY_EXIT",
            "reason": decision.exit_reason or "STRATEGY_EXIT",
            "confidence": decision.confidence,
            "explanation": decision.explanation,
            "exit_price": current_price,
        }

        return None

    def _normalize_strategy_decision(self, value: Any) -> ExitDecision | None:
        if value is None:
            return None
        if isinstance(value, ExitDecision):
            return value
        if isinstance(value, dict):
            return ExitDecision(
                should_exit=bool(value.get("should_exit", False)),
                exit_reason=str(value.get("exit_reason") or "STRATEGY_EXIT"),
                confidence=float(value.get("confidence", 0.0) or 0.0),
                explanation=str(value.get("explanation") or ""),
                exit_type=str(value.get("exit_type") or "STRATEGY_EXIT"),
            )
        return None

    def _execute_exit(self, position: Any, *, decision: dict[str, Any]) -> Any:
        old_summary = self.portfolio_engine.get_summary()
        old_portfolio_value = float(old_summary.get("portfolio_value", 0.0) or 0.0)
        exit_price = float(decision.get("exit_price") or getattr(position, "current_price", 0.0) or 0.0)
        reason = str(decision.get("reason") or decision.get("type") or "MANUAL_EXIT")
        explanation = str(decision.get("explanation") or "")
        closed = self.portfolio_engine.close_position(
            position.symbol,
            exit_price=exit_price,
            reason=reason,
            exit_explanation=explanation,
        )
        if closed is None:
            return None

        new_summary = self.portfolio_engine.get_summary()
        new_portfolio_value = float(new_summary.get("portfolio_value", 0.0) or 0.0)
        current_stats = asdict(self.portfolio_engine.get_statistics())
        payload_snapshot = self._build_journal_payload(
            position=position,
            closed=closed,
            decision=decision,
            summary=new_summary,
            stats=current_stats,
            old_portfolio_value=old_portfolio_value,
            new_portfolio_value=new_portfolio_value,
        )

        event_name = {
            "STOP_LOSS": "STOP_LOSS_TRIGGERED",
            "TAKE_PROFIT": "TARGET_TRIGGERED",
            "STRATEGY_EXIT": "STRATEGY_EXIT",
            "MANUAL_EXIT": "MANUAL_EXIT",
            "EMERGENCY_CLOSE": "EMERGENCY_CLOSE",
            "END_OF_SESSION": "END_OF_SESSION",
            "END_OF_TEST": "END_OF_TEST",
        }.get(str(decision.get("type")), "POSITION_CLOSED")

        self.portfolio_engine.record_audit_event(
            event_name,
            utc_timestamp=self._utc_now(),
            position_id=position.position_id,
            trade_id=getattr(closed, "trade_id", ""),
            decision_id=getattr(position, "decision_id", ""),
            symbol=position.symbol,
            old_portfolio_value=old_portfolio_value,
            new_portfolio_value=new_portfolio_value,
            reason=reason,
            confidence=float(decision.get("confidence", 0.0) or 0.0),
            explanation=explanation,
        )
        self.portfolio_engine.record_audit_event(
            "POSITION_CLOSED",
            utc_timestamp=self._utc_now(),
            position_id=position.position_id,
            trade_id=getattr(closed, "trade_id", ""),
            decision_id=getattr(position, "decision_id", ""),
            symbol=position.symbol,
            old_portfolio_value=old_portfolio_value,
            new_portfolio_value=new_portfolio_value,
            reason=reason,
            explanation=explanation,
        )
        self.portfolio_engine.record_audit_event(
            "TRADE_JOURNAL_EVENT",
            utc_timestamp=self._utc_now(),
            event_type="CLOSED_TRADE",
            position_id=position.position_id,
            trade_id=getattr(closed, "trade_id", ""),
            decision_id=getattr(position, "decision_id", ""),
            strategy_id=getattr(position, "strategy_id", ""),
            strategy_name=getattr(position, "strategy_name", ""),
            payload=payload_snapshot,
        )
        self.portfolio_engine.record_audit_event(
            "PERFORMANCE_EVENT",
            utc_timestamp=self._utc_now(),
            event_type="CLOSED_TRADE",
            position_id=position.position_id,
            trade_id=getattr(closed, "trade_id", ""),
            decision_id=getattr(position, "decision_id", ""),
            old_portfolio_value=old_portfolio_value,
            new_portfolio_value=new_portfolio_value,
            net_profit=float(getattr(closed, "net_profit", 0.0) or 0.0),
        )

        self.portfolio_engine.record_audit_event(
            "PORTFOLIO_UPDATED",
            utc_timestamp=self._utc_now(),
            position_id=position.position_id,
            trade_id=getattr(closed, "trade_id", ""),
            decision_id=getattr(position, "decision_id", ""),
            old_portfolio_value=old_portfolio_value,
            new_portfolio_value=new_portfolio_value,
        )
        return closed

    def _build_journal_payload(
        self,
        *,
        position: Any,
        closed: Any,
        decision: dict[str, Any],
        summary: dict[str, Any],
        stats: dict[str, Any],
        old_portfolio_value: float,
        new_portfolio_value: float,
    ) -> dict[str, Any]:
        closed_data = asdict(closed)
        entry_price = float(getattr(position, "entry_price", closed_data.get("entry_price", 0.0)) or 0.0)
        exit_price = float(closed_data.get("exit_price", 0.0) or 0.0)
        quantity = int(closed_data.get("quantity", 0) or 0)
        net_profit = float(closed_data.get("net_profit", 0.0) or 0.0)
        gross_profit = float(closed_data.get("gross_profit", 0.0) or 0.0)

        decision_score = float(decision.get("confidence", 0.0) or 0.0)
        reasons = [
            str(decision.get("reason") or ""),
            str(decision.get("explanation") or ""),
        ]
        reasons = [item for item in reasons if item]

        risk_amount = float(getattr(position, "risk", 0.0) or 0.0)
        risk_percent = 0.0
        if old_portfolio_value > 0:
            risk_percent = round((risk_amount / old_portfolio_value) * 100.0, 4)

        risk_distance = abs(float(getattr(position, "entry_price", 0.0) or 0.0) - float(getattr(position, "stop_loss", 0.0) or 0.0))
        reward_distance = abs(float(getattr(position, "target", 0.0) or 0.0) - float(getattr(position, "entry_price", 0.0) or 0.0))
        reward_risk_ratio = 0.0
        if risk_distance > 0:
            reward_risk_ratio = round(reward_distance / risk_distance, 4)

        closed_trades = self.portfolio_engine.get_closed_trades()
        strategy_closed = [
            item
            for item in closed_trades
            if str(getattr(item, "strategy_id", "") or "") == str(getattr(position, "strategy_id", "") or "")
        ]
        strategy_wins = [item for item in strategy_closed if float(getattr(item, "net_profit", 0.0) or 0.0) > 0]
        strategy_win_rate = 0.0
        if strategy_closed:
            strategy_win_rate = round((len(strategy_wins) / len(strategy_closed)) * 100.0, 2)

        winning_profits = [float(getattr(item, "net_profit", 0.0) or 0.0) for item in closed_trades if float(getattr(item, "net_profit", 0.0) or 0.0) > 0]
        losing_profits = [abs(float(getattr(item, "net_profit", 0.0) or 0.0)) for item in closed_trades if float(getattr(item, "net_profit", 0.0) or 0.0) < 0]
        profit_factor = inf if winning_profits and not losing_profits else 0.0
        if losing_profits:
            profit_factor = round(sum(winning_profits) / sum(losing_profits), 4) if winning_profits else 0.0

        drawdown = 0.0
        if old_portfolio_value > 0 and new_portfolio_value < old_portfolio_value:
            drawdown = round(((old_portfolio_value - new_portfolio_value) / old_portfolio_value) * 100.0, 4)

        market_snapshot = {
            "timeframe": "",
            "trend": "",
            "rsi": None,
            "ema12": None,
            "ema26": None,
            "macd": None,
            "atr": None,
            "volume": None,
            "indicators": {
                "distance_to_stop_loss": float(getattr(position, "distance_to_stop_loss", 0.0) or 0.0),
                "distance_to_target": float(getattr(position, "distance_to_target", 0.0) or 0.0),
                "price_status": str(getattr(position, "price_status", "LIVE") or "LIVE"),
            },
        }

        supporting_evidence = [
            f"Entry {entry_price} Exit {exit_price} Qty {quantity}",
            f"Reason {str(closed_data.get('exit_reason', '') or '')}",
            f"Explanation {str(closed_data.get('exit_explanation', '') or '')}",
        ]

        payload = {
            **closed_data,
            "asset_class": "EQUITY",
            "decision_snapshot": {
                "decision_score": decision_score,
                "confidence": decision_score,
                "technical_score": decision_score,
                "strategy_score": decision_score,
                "risk_score": round(float(stats.get("cash_allocation", 0.0) or 0.0), 4),
                "portfolio_score": round(float(stats.get("portfolio_return_percent", 0.0) or 0.0), 4),
                "market_score": decision_score,
                "reasons": reasons,
            },
            "risk_snapshot": {
                "risk_percent": risk_percent,
                "position_size": float(quantity),
                "capital_at_risk": round(risk_amount, 4),
                "reward_risk_ratio": reward_risk_ratio,
                "stop_loss": float(getattr(position, "stop_loss", 0.0) or 0.0),
                "target": float(getattr(position, "target", 0.0) or 0.0),
            },
            "performance_snapshot": {
                "win_loss": "WIN" if net_profit > 0 else "LOSS",
                "profit_factor_at_trade_time": float(profit_factor),
                "running_equity": float(summary.get("portfolio_value", new_portfolio_value) or new_portfolio_value),
                "running_drawdown": drawdown,
                "strategy_win_rate": strategy_win_rate,
                "portfolio_win_rate": float(stats.get("win_rate", 0.0) or 0.0),
            },
            "market_snapshot": market_snapshot,
            "supporting_evidence": supporting_evidence,
            "audit_events": [
                {
                    "event": "EXIT_EXECUTED",
                    "timestamp": self._utc_now(),
                    "details": {
                        "position_id": getattr(position, "position_id", ""),
                        "trade_id": closed_data.get("trade_id", ""),
                        "decision_id": getattr(position, "decision_id", ""),
                        "gross_profit": gross_profit,
                        "net_profit": net_profit,
                    },
                }
            ],
        }
        return payload

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")