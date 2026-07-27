"""
===========================================================
TradePilotAI
Optimisation Report
===========================================================

Formats and ranks optimisation results.
"""

from __future__ import annotations

from optimisation.optimisation_result import (
    OptimisationResult,
)


class OptimisationReport:
    """
    Provides reporting and ranking for optimisation runs.
    """

    def __init__(
        self,
        results: list[OptimisationResult],
    ) -> None:

        self._results = results


    @property
    def results(self) -> list[OptimisationResult]:
        """
        Return optimisation results.
        """

        return self._results.copy()


    @property
    def ranked_results(
        self,
    ) -> list[OptimisationResult]:
        """
        Return results ranked by score.
        """

        return sorted(
            self._results,
            key=lambda result: result.score,
            reverse=True,
        )


    @property
    def best_result(
        self,
    ) -> OptimisationResult | None:
        """
        Return the highest scoring result.
        """

        if not self._results:

            return None


        return self.ranked_results[0]


    def top(
        self,
        count: int = 5,
    ) -> list[OptimisationResult]:
        """
        Return top performing configurations.
        """

        return self.ranked_results[:count]


    def to_text(self) -> str:
        """
        Return a formatted optimisation report.
        """

        if not self._results:

            return (
                "No optimisation results available."
            )


        lines = [

            "================================================",

            "TradePilotAI Optimisation Report",

            "================================================",

            "",

            "Rank | Score | Profit | Win Rate | Drawdown | Parameters",

            "------------------------------------------------",

        ]


        for index, result in enumerate(
            self.ranked_results,
            start=1,
        ):

            lines.append(

                f"{index} | "
                f"{result.score:.2f} | "
                f"{result.net_profit:.2f} | "
                f"{result.win_rate:.2f}% | "
                f"{result.max_drawdown:.2f}% | "
                f"{result.parameters}"

            )


        return "\n".join(lines)


    def __str__(self) -> str:

        return self.to_text()