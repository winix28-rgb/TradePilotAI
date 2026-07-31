"""Risk Dashboard workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import Card, SectionHeader, StatusBadge, StatusBar, Toolbar
from tradepilotai_os.workspace import WorkspacePage

from .components import ExposureCard, PositionRiskTable, RiskKpiCard, RiskRulesCard, RiskTimelineCard
from .data_provider import RiskDataProvider


class RiskDashboardPage(WorkspacePage):
    """Render the portfolio and trading risk dashboard workspace."""

    def __init__(self, data_provider: RiskDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Risk", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_risk_data()
        else:
            self.data = {"assessment": {}, "exposures": [], "positions": [], "rules": [], "violations": [], "timeline": [], "events": []}

        assessment = self.data.get("assessment", {})
        exposures = self.data.get("exposures", [])
        positions = self.data.get("positions", [])
        rules = self.data.get("rules", [])
        violations = self.data.get("violations", [])
        timeline = self.data.get("timeline", [])
        events = self.data.get("events", [])

        lines = [
            "",
            "=" * 80,
            "RISK DASHBOARD",
            "=" * 80,
            "",
            self.build_title("Risk Overview", "Portfolio & position risk"),
            "",
            self.build_toolbar("Risk Controls", ["Assess", "Refresh", "Export"]),
            "",
            self.build_breadcrumbs("risk", "Risk"),
            "",
            StatusBadge(label="Risk", status="live").render(),
            "",
            RiskKpiCard(title="Portfolio Risk Score", value=str(assessment.get("portfolio_risk_score", 0)), subtitle="score").render(),
            RiskKpiCard(title="Total Exposure", value=f"${assessment.get('total_exposure', 0):,.0f}", subtitle="exposure").render(),
            RiskKpiCard(title="Available Cash", value=f"${assessment.get('available_cash', 0):,.0f}", subtitle="cash").render(),
            RiskKpiCard(title="Buying Power", value=f"${assessment.get('buying_power', 0):,.0f}", subtitle="buying power").render(),
            RiskKpiCard(title="Largest Position", value=str(assessment.get("largest_position", "N/A")), subtitle="largest").render(),
            RiskKpiCard(title="Daily Risk", value=f"${assessment.get('daily_risk', 0):,.0f}", subtitle="daily").render(),
            RiskKpiCard(title="Maximum Drawdown", value=str(assessment.get("max_drawdown", 0)), subtitle="drawdown").render(),
            RiskKpiCard(title="Value at Risk", value=f"${assessment.get('value_at_risk', 0):,.0f}", subtitle="var").render(),
            RiskKpiCard(title="Open Positions", value=str(assessment.get("open_positions", 0)), subtitle="count").render(),
            "",
            ExposureCard(exposures=exposures).render(),
            "",
            PositionRiskTable(rows=positions).render(),
            "",
            RiskRulesCard(rules=rules).render(),
            "",
            RiskTimelineCard(events=timeline).render(),
            "",
            Card(title="Risk Events", body=[f"{item['name']}: {item.get('details', '')}" for item in violations]).render(),
            "",
            Card(title="Recent Events", body=[f"{item['name']}: {item.get('details', '')}" for item in events]).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "risk"
        items = ["Dashboard", "Risk"]
        if current_route and current_route != "risk":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
