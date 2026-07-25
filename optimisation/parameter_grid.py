"""
===========================================================
TradePilotAI
Parameter Grid
===========================================================

Generates all parameter combinations for strategy
optimisation.
"""

from __future__ import annotations

from itertools import product


class ParameterGrid:
    """
    Generates every possible parameter combination.
    """

    def __init__(
        self,
        parameters: dict[str, list[int | float]],
    ) -> None:

        self._parameters = parameters

    def generate(self) -> list[dict[str, int | float]]:
        """
        Return every parameter combination.
        """

        if not self._parameters:
            return []

        names = list(self._parameters.keys())

        values = [
            self._parameters[name]
            for name in names
        ]

        combinations = []

        for combination in product(*values):

            combinations.append(
                dict(zip(names, combination))
            )

        return combinations

    def __len__(self) -> int:
        """
        Number of combinations.
        """

        return len(self.generate())