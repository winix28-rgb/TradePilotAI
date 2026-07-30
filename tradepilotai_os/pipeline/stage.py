"""Abstract stage interface for pipeline execution."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .context import PipelineContext


class PipelineStage(ABC):
    """Abstract base class for a single pipeline stage.

    Each stage receives the shared context, performs work, and may
    mutate the context in place.
    """

    @abstractmethod
    def execute(self, context: PipelineContext) -> None:
        """Execute the stage using the provided pipeline context."""
