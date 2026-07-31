"""Event models for scanner workspaces."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScannerEvent:
    """Represents a scanner lifecycle event."""

    name: str
    status: str
    payload: dict[str, object] | None = None
