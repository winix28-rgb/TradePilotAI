"""Signal pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class SignalStage(PipelineStage):
    """Wrap a signal service as a pipeline stage."""

    def __init__(self, signal_service: Any) -> None:
        self._signal_service = signal_service

    def execute(self, context: PipelineContext) -> None:
        """Populate the context with signals derived from the data."""

        data = context.get("data")
        symbol = context.get("symbol")
        if data is None or symbol is None:
            return

        signals = self._signal_service.find_signals(data, symbol)
        context.set("signals", signals)

        summary = context.get("summary", {})
        summary["signals_generated"] = summary.get("signals_generated", 0) + len(signals)
        context.set("summary", summary)
