"""Scanner workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import (
    Card,
    SectionHeader,
    StatusBadge,
    StatusBar,
    Toolbar,
)
from tradepilotai_os.workspace import WorkspacePage

from .components import (
    ScannerBuyCandidatesTable,
    ScannerPipelineStatus,
    ScannerSignalDetail,
    ScannerSummaryCard,
    ScannerWatchListTable,
)
from .data_provider import ScannerDataProvider


class ScannerPage(WorkspacePage):
    """Render the scanner workspace page inside the application shell."""

    def __init__(self, data_provider: ScannerDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Scanner", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_scanner_data()
        else:
            self.data = {
                "summary": {},
                "pipeline": {},
                "buy_candidates": [],
                "sell_candidates": [],
                "watch_list": [],
                "signal_detail": {},
                "events": [],
            }

        summary = self.data.get("summary", {})
        pipeline = self.data.get("pipeline", {})
        buy_candidates = self.data.get("buy_candidates", [])
        sell_candidates = self.data.get("sell_candidates", [])
        watch_list = self.data.get("watch_list", [])
        signal_detail = self.data.get("signal_detail", {})
        events = self.data.get("events", [])

        lines = [
            "",
            "=" * 80,
            "SCANNER WORKSPACE",
            "=" * 80,
            "",
            self.build_title("Scanner Overview", "Trading opportunity workspace"),
            "",
            self.build_toolbar("Scanner Controls", ["Scan", "Refresh"]),
            "",
            self.build_breadcrumbs("scanner", "Scanner"),
            "",
            StatusBadge(label="Scanner", status="live").render(),
            "",
            ScannerSummaryCard(summary=summary).render(),
            "",
            ScannerPipelineStatus(pipeline=pipeline).render(),
            "",
            ScannerBuyCandidatesTable(rows=buy_candidates).render(),
            "",
            ScannerBuyCandidatesTable(rows=sell_candidates, title="Sell Candidates").render(),
            "",
            ScannerWatchListTable(rows=watch_list).render(),
            "",
            ScannerSignalDetail(detail=signal_detail).render(),
            "",
            Card(title="Scanner Events", body=[f"{event['name']}: {event['status']}" for event in events]).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "scanner"
        items = ["Dashboard", "Scanner"]
        if current_route and current_route != "scanner":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
