"""Strategy Centre workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import Card, SectionHeader, StatusBadge, StatusBar, Toolbar
from tradepilotai_os.workspace import WorkspacePage

from .components import DeploymentCard, PerformanceSummaryCard, StrategyConfigurationCard, StrategyLibraryTable, StrategySummaryCard, VersionHistoryCard
from .data_provider import StrategyDataProvider


class StrategyPage(WorkspacePage):
    """Render the professional Strategy Centre workspace."""

    def __init__(self, data_provider: StrategyDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Strategy Centre", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_strategy_data()
        else:
            self.data = {"strategies": [], "current_strategy": None, "events": []}

        strategy = self.data.get("current_strategy") or {}
        strategies = self.data.get("strategies", [])
        versions = strategy.get("versions", [])
        config = strategy.get("configuration", {})
        performance = strategy.get("performance", {})
        deployment = strategy.get("deployment") or {"target": "Paper Broker", "status": "Pending", "broker_interface": "Broker Interface", "orchestrator": "Application Orchestrator"}

        lines = [
            "",
            "=" * 80,
            "STRATEGY CENTRE",
            "=" * 80,
            "",
            self.build_title("Strategy Library", "Create, configure, version, and deploy strategies"),
            "",
            self.build_toolbar("Strategy Controls", ["Create Strategy", "Create Version", "Deploy", "Refresh"]),
            "",
            self.build_breadcrumbs("strategy", "Strategy Centre"),
            "",
            StatusBadge(label="Strategy Centre", status="active").render(),
            "",
            StrategySummaryCard(title="Strategy", value=strategy.get("name", "N/A"), subtitle=strategy.get("status", "Draft")).render(),
            StrategySummaryCard(title="Version", value=strategy.get("version", "N/A"), subtitle="current version").render(),
            StrategySummaryCard(title="Markets", value=strategy.get("markets", "FX"), subtitle="supported markets").render(),
            StrategySummaryCard(title="Timeframe", value=strategy.get("timeframe", "1H"), subtitle="timeframe").render(),
            "",
            StrategyLibraryTable(rows=strategies).render(),
            "",
            StrategyConfigurationCard(config=config).render(),
            "",
            PerformanceSummaryCard(performance=performance).render(),
            "",
            VersionHistoryCard(versions=versions).render(),
            "",
            DeploymentCard(deployment=deployment).render(),
            "",
            Card(title="Strategy Events", body=[f"{item}" for item in self.data.get("events", [])]).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "strategy"
        items = ["Dashboard", "Strategy Centre"]
        if current_route and current_route != "strategy":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
