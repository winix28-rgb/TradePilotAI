"""Generic trading pipeline wrapper for the TradePilotAI OS."""

from __future__ import annotations

from typing import Sequence

from .base import BasePipeline
from .context import PipelineContext
from .stage import PipelineStage


class TradingPipeline(BasePipeline):
    """A generic pipeline for orchestrating a trading workflow.

    This class inherits from BasePipeline and accepts stages through
    dependency injection. It does not construct concrete scanners,
    brokers, indicators, or strategies itself, keeping the pipeline
    independent from specific implementations.
    """

    def __init__(self, stages: Sequence[PipelineStage] | None = None) -> None:
        super().__init__(stages=stages)

    def run(self, context: PipelineContext | None = None) -> PipelineContext:
        """Execute the configured stages using the provided context."""

        return super().run(context=context)
