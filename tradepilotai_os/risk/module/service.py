"""Service layer for the Risk Dashboard workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk.risk_engine import RiskEngine

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

    def __init__(
        self,
        event_bus: EventBus | None = None,
        portfolio_manager: PortfolioManager | None = None,
        broker: PaperBroker | None = None,
        risk_engine: RiskEngine | None = None,
    ) -> None:
        self.event_bus = event_bus or EventBus()
        self.portfolio_manager = portfolio_manager
        self.broker = broker
        self.risk_engine = risk_engine
        self._refresh_count = 0
        self._events: list[RiskEvent] = []

    def get_snapshot(self) -> RiskSnapshot:
        portfolio_state = getattr(self.portfolio_manager, "state", None)
        broker_portfolio = getattr(self.broker, "portfolio", None) if self.broker is not None else None
        portfolio_source = portfolio_state if portfolio_state is not None else broker_portfolio

        cash = 0.0
        exposure = 0.0
        unrealised_pnl = 0.0
        realised_pnl = 0.0
        positions: dict[str, Any] = {}
        if portfolio_source is not None:
            cash = float(getattr(portfolio_source, "cash", 0.0) or 0.0)
            exposure = float(getattr(portfolio_source, "exposure", 0.0) or 0.0)
            unrealised_pnl = float(getattr(portfolio_source, "unrealised_pnl", 0.0) or 0.0)
            realised_pnl = float(getattr(portfolio_source, "realised_pnl", 0.0) or 0.0)
            positions = getattr(portfolio_source, "positions", {}) or {}

        if portfolio_state is None and broker_portfolio is not None and isinstance(broker_portfolio, object):
            cash = float(getattr(broker_portfolio, "cash", 0.0) or 0.0)
            exposure = float(getattr(broker_portfolio, "exposure", 0.0) or 0.0)
            unrealised_pnl = float(getattr(broker_portfolio, "unrealised_pnl", 0.0) or 0.0)
            realised_pnl = float(getattr(broker_portfolio, "realised_pnl", 0.0) or 0.0)
            positions = getattr(broker_portfolio, "positions", {}) or {}

        position_items = list(positions.items()) if isinstance(positions, dict) else []
        open_positions = len(position_items)
        largest_position = "N/A"
        largest_weight = 0.0
        risk_rows: list[PositionRisk] = []
        for symbol, position in position_items:
            if getattr(position, "quantity", 0) <= 0:
                continue
            market_price = float(getattr(position, "market_price", 0.0) or 0.0)
            average_price = float(getattr(position, "average_price", 0.0) or 0.0)
            exposure_value = float(getattr(position, "exposure", 0.0) or 0.0)
            if exposure_value > largest_weight:
                largest_weight = exposure_value
                largest_position = symbol
            if exposure > 0:
                weight_percent = (exposure_value / exposure * 100.0) if exposure else 0.0
            else:
                weight_percent = 0.0
            stop_distance = abs(market_price - average_price) if market_price and average_price else 0.0
            risk_percent = round(weight_percent, 2)
            risk_rows.append(
                PositionRisk(
                    symbol=symbol,
                    position_size=float(getattr(position, "quantity", 0) or 0.0),
                    risk_percent=risk_percent,
                    stop_distance=stop_distance,
                    unrealised_pnl=float((market_price - average_price) * getattr(position, "quantity", 0)) if market_price and average_price else 0.0,
                    exposure_percent=round(weight_percent, 2),
                    risk_rating="High" if risk_percent >= 20.0 else "Medium" if risk_percent >= 10.0 else "Low",
                )
            )

        total_value = cash + unrealised_pnl + exposure
        if total_value <= 0:
            total_value = 100000.0

        portfolio_risk_score = round(min(100.0, max(0.0, (exposure / total_value) * 100.0)), 2)
        daily_risk = round(exposure * 0.02, 2)
        max_drawdown = round((realised_pnl + unrealised_pnl) / max(total_value, 1.0) * 100.0, 2)
        value_at_risk = round(exposure * 0.01, 2)
        buying_power = max(0.0, cash - exposure)
        available_cash = cash

        assessment = RiskAssessment(
            portfolio_risk_score=portfolio_risk_score,
            total_exposure=exposure,
            available_cash=available_cash,
            buying_power=buying_power,
            largest_position=largest_position,
            daily_risk=daily_risk,
            max_drawdown=max_drawdown,
            value_at_risk=value_at_risk,
            open_positions=open_positions,
            summary="Live portfolio risk snapshot",
        )
        exposures = [
            PortfolioExposure(label="Cash", value=available_cash, category="Liquidity"),
            PortfolioExposure(label="Exposure", value=exposure, category="Portfolio"),
        ]
        if risk_rows:
            exposures.append(PortfolioExposure(label="Largest Position", value=largest_weight, category="Position"))
        rules = [
            RiskRule(name="Max Risk Per Trade", current_value=round(max(0.0, min(100.0, (exposure / max(total_value, 1.0)) * 100.0)), 2), configured_limit=2.0, status="OK"),
            RiskRule(name="Max Portfolio Exposure", current_value=round((exposure / max(total_value, 1.0)) * 100.0, 2), configured_limit=70.0, status="OK"),
            RiskRule(name="Max Open Positions", current_value=float(open_positions), configured_limit=6.0, status="Warning" if open_positions >= 6 else "OK"),
            RiskRule(name="Daily Loss Limit", current_value=daily_risk, configured_limit=4000.0, status="OK"),
        ]
        violations = []
        if open_positions >= 6:
            violations.append(RiskViolation(name="Risk Limit Breached", details="Open position count exceeds policy limit", severity="Warning"))
        timeline = [
            {"event": "Portfolio snapshot refreshed", "time": "live"},
        ]
        return RiskSnapshot(
            assessment=assessment,
            exposures=exposures,
            positions=risk_rows,
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
