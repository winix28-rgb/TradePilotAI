"""Strongly typed execution context for pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import time


@dataclass(slots=True)
class PipelineContext:
    """Shared container for pipeline execution state.

    The context is intentionally framework-focused and carries typed
    execution fields, optional metadata, timing information, and
    error tracking for stages to consume or update.
    """

    status: str = "created"
    current_stage: Optional[str] = None
    completed_stages: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    last_error: Optional[str] = None
    error_count: int = 0

    def __post_init__(self) -> None:
        """Initialize timing state when the context is created."""

        self.started_at = self.started_at or time.time()

    def mark_started(self) -> None:
        """Record the start timestamp if it has not already been set."""

        if self.started_at is None:
            self.started_at = time.time()

    def mark_completed(self) -> None:
        """Record the completion timestamp."""

        self.completed_at = time.time()
        self.status = "completed"

    def mark_failed(self, error: str) -> None:
        """Record an execution failure and increment the error counter."""

        self.last_error = error
        self.error_count += 1
        self.status = "failed"

    def set_metadata(self, key: str, value: Any) -> None:
        """Store arbitrary extension data on the context."""

        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Retrieve extension data from the context metadata store."""

        return self.metadata.get(key, default)
