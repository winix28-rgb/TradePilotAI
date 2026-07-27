"""
===========================================================
TradePilotAI
Maximum Position Manager
===========================================================

Controls the maximum number of open positions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MaxPositionManager:
    """
    Controls portfolio position limits.
    """

    maximum_positions: int = 10


    def __post_init__(self):

        if self.maximum_positions < 1:
            raise ValueError(
                "maximum_positions must be at least 1"
            )


    def can_open_position(
        self,
        current_positions: int,
    ) -> bool:
        """
        Determine whether another position can be opened.
        """

        if current_positions < 0:
            raise ValueError(
                "current_positions cannot be negative"
            )

        return (
            current_positions
            <
            self.maximum_positions
        )


    def remaining_capacity(
        self,
        current_positions: int,
    ) -> int:
        """
        Return remaining available positions.
        """

        if current_positions < 0:
            raise ValueError(
                "current_positions cannot be negative"
            )

        return max(
            self.maximum_positions - current_positions,
            0,
        )