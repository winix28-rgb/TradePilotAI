"""Scanner pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class ScannerStage(PipelineStage):
    """Wrap a scanner service as a pipeline stage."""

    def __init__(self, scanner: Any) -> None:
        self._scanner = scanner

    def execute(self, context: PipelineContext) -> None:
        """Populate the context with the scanner watchlist."""

        watchlist = self._scanner.get_watchlist()
        context.set("watchlist", watchlist)

        summary = context.get("summary", {})
        summary["symbols_scanned"] = summary.get("symbols_scanned", 0) + 1
        context.set("summary", summary)
