"""Parameter and schema models for the backtesting strategy library."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(frozen=True, slots=True)
class StrategyParameter:
    """Typed strategy parameter definition for dynamic UI rendering."""

    key: str
    label: str
    param_type: str
    default: Any
    description: str = ""
    minimum: float | None = None
    maximum: float | None = None
    step: float | None = None
    options: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "type": self.param_type,
            "default": self.default,
            "description": self.description,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
            "options": list(self.options),
        }
