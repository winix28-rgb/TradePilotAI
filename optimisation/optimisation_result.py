"""
===========================================================
TradePilotAI
Optimisation Result
===========================================================

Represents the outcome of a single optimisation run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class OptimisationResult:
    """
    Represents the performance of a single
    strategy parameter set.
    """

    parameters: dict[str, float | int]

    net_profit: float

    win_rate: float

    profit_factor: float

    max_drawdown: float

    expectancy: float

    total_trades: int

    @property
    def score(self) -> float:
        """
        Default optimisation score.

        Higher is better.

        Formula:

            Profit Factor
                ×
            (100 - Drawdown%)
        """

        return (
            self.profit_factor
            * (100 - self.max_drawdown)
        )