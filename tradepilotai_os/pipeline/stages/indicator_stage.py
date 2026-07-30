"""Indicator pipeline stage."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.pipeline.context import PipelineContext
from tradepilotai_os.pipeline.stage import PipelineStage


class IndicatorStage(PipelineStage):
    """Wrap an indicator service as a pipeline stage."""

    def __init__(self, indicator_service: Any) -> None:
        self._indicator_service = indicator_service

    def execute(self, context: PipelineContext) -> None:
        """Attach indicator values to the data in the context."""

        data = context.get("data")
        if data is None:
            return

        context.set("data", self._indicator_service.add_indicators(data))
