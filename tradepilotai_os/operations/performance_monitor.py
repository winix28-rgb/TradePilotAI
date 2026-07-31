"""Lightweight performance monitor for operational review."""

from __future__ import annotations

from collections import Counter
from time import perf_counter
from typing import Any


class PerformanceMonitor:
    """Track refresh and service call counts to avoid unnecessary work."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._timings: dict[str, list[float]] = {}

    def record(self, name: str, duration: float | None = None) -> None:
        self._counts[name] += 1
        if duration is not None:
            self._timings.setdefault(name, []).append(duration)

    def counts(self) -> dict[str, int]:
        return dict(self._counts)

    def average_duration(self, name: str) -> float:
        timings = self._timings.get(name, [])
        if not timings:
            return 0.0
        return sum(timings) / len(timings)

    def time_call(self, name: str, func: Any, *args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            self.record(name, perf_counter() - start)
