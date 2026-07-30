"""Base pipeline implementation for orchestrating stages."""

from __future__ import annotations

from typing import Sequence

from .context import PipelineContext
from .stage import PipelineStage


class BasePipeline:
    """Execute a sequence of pipeline stages in order.

    The pipeline passes the same context object through each stage,
    allowing later stages to consume or extend the shared state.
    """

    def __init__(self, stages: Sequence[PipelineStage] | None = None) -> None:
        self._stages = list(stages or [])

    def add_stage(self, stage: PipelineStage) -> None:
        """Append a stage to the pipeline."""

        self._stages.append(stage)

    def run(self, context: PipelineContext | None = None) -> PipelineContext:
        """Execute all registered stages using the supplied context."""

        pipeline_context = context or PipelineContext()
        for stage in self._stages:
            stage.execute(pipeline_context)
        return pipeline_context
