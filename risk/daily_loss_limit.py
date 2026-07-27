"""
===========================================================
TradePilotAI
Daily Loss Limit
===========================================================

Prevents trading after the maximum daily loss has been
reached.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DailyLossLimit:
    """
    Controls maximum daily losses.
    """

    starting_balance: float

    max_loss_percent: float = 2.0


    def __post_init__(self):

        if self.starting_balance <= 0:
            raise ValueError(
                "Starting balance must be greater than zero."
            )


        if self.max_loss_percent <= 0:
            raise ValueError(
                "Maximum loss percent must be greater than zero."
            )


    @property
    def maximum_loss(self) -> float:
        """
        Maximum permitted loss amount.
        """

        return (
            self.starting_balance
            *
            self.max_loss_percent
            /
            100
        )


    def trading_allowed(
        self,
        current_balance: float,
    ) -> bool:
        """
        Check if trading can continue.
        """

        loss = (
            self.starting_balance
            -
            current_balance
        )

        return loss < self.maximum_loss