"""Data pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class DataStage(PipelineStage):
    """Wrap a data engine service as a pipeline stage."""

    def __init__(self, data_engine: Any) -> None:
        self._data_engine = data_engine

    def execute(self, context: PipelineContext) -> None:
        """Load market data for the current symbol into the context."""

        symbol = context.get("symbol")
        interval = context.get("interval", "1d")
        period = context.get("period", "180d")
        if symbol is None:
            return

        context.set("data", self._data_engine.download_data(symbol, interval=interval, period=period))
