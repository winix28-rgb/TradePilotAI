"""
===========================================================
TradePilotAI
Position Reconciler
===========================================================

Compares internal portfolio positions against broker
positions to detect mismatches.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PositionReconciliationResult:
    """
    Result of a position reconciliation check.
    """

    matched: bool

    missing_positions: list[str]

    unexpected_positions: list[str]



class PositionReconciler:
    """
    Checks that internal and broker positions agree.
    """


    def reconcile(
        self,
        internal_positions: list[str],
        broker_positions: list[str],
    ) -> PositionReconciliationResult:
        """
        Compare internal positions against broker positions.
        """

        internal = set(
            internal_positions
        )

        broker = set(
            broker_positions
        )


        missing = list(
            internal - broker
        )

        unexpected = list(
            broker - internal
        )


        return PositionReconciliationResult(

            matched=(
                len(missing) == 0
                and
                len(unexpected) == 0
            ),

            missing_positions=missing,

            unexpected_positions=unexpected,

        )