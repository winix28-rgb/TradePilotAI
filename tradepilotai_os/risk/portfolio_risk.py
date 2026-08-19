"""
===========================================================
TradePilotAI OS
Portfolio Risk Controller
===========================================================

Controls the total risk committed across currently open
trades.

Agreed S&D portfolio rules:

    Maximum open trades: 5
    Maximum total portfolio risk: 5%

This component does not:
    - create trades
    - calculate stop losses
    - calculate take profits
    - communicate with a broker

It only determines whether a proposed trade can be added
to the currently open portfolio.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioRiskAssessment:
    """Result of a portfolio-risk assessment."""

    permitted: bool
    reason: str

    current_open_trades: int
    current_risk_value: float

    proposed_risk_value: float
    total_risk_value: float

    current_risk_percent: float
    proposed_risk_percent: float
    total_risk_percent: float


class PortfolioRiskController:
    """
    Enforce the maximum number of open trades and total
    portfolio risk.
    """

    def __init__(
        self,
        portfolio_value: float = 100000.0,
        max_risk_percent: float = 5.0,
        max_open_trades: int = 5,
    ) -> None:

        if portfolio_value <= 0:
            raise ValueError(
                "Portfolio value must be greater than zero."
            )

        if max_risk_percent <= 0:
            raise ValueError(
                "Maximum risk percentage must be greater than zero."
            )

        if max_open_trades <= 0:
            raise ValueError(
                "Maximum open trades must be greater than zero."
            )

        self.portfolio_value = float(portfolio_value)
        self.max_risk_percent = float(max_risk_percent)
        self.max_open_trades = int(max_open_trades)

    @property
    def max_risk_value(self) -> float:
        """Maximum monetary risk allowed across open trades."""

        return (
            self.portfolio_value
            * self.max_risk_percent
            / 100.0
        )

    def assess(
        self,
        current_open_trades: int,
        current_risk_value: float,
        proposed_risk_value: float,
    ) -> PortfolioRiskAssessment:
        """
        Determine whether a new trade can be opened.

        The proposed trade is assessed BEFORE it is added to
        the open portfolio.
        """

        if current_open_trades < 0:
            raise ValueError(
                "Current open trades cannot be negative."
            )

        if current_risk_value < 0:
            raise ValueError(
                "Current risk value cannot be negative."
            )

        if proposed_risk_value <= 0:
            raise ValueError(
                "Proposed risk value must be greater than zero."
            )

        total_open_trades = current_open_trades + 1

        total_risk_value = (
            current_risk_value
            + proposed_risk_value
        )

        current_risk_percent = (
            current_risk_value
            / self.portfolio_value
            * 100.0
        )

        proposed_risk_percent = (
            proposed_risk_value
            / self.portfolio_value
            * 100.0
        )

        total_risk_percent = (
            total_risk_value
            / self.portfolio_value
            * 100.0
        )

        # -----------------------------------------------------
        # Maximum number of open trades
        # -----------------------------------------------------

        if total_open_trades > self.max_open_trades:
            return PortfolioRiskAssessment(
                permitted=False,
                reason=(
                    "Maximum number of open trades would "
                    "be exceeded."
                ),
                current_open_trades=current_open_trades,
                current_risk_value=current_risk_value,
                proposed_risk_value=proposed_risk_value,
                total_risk_value=total_risk_value,
                current_risk_percent=current_risk_percent,
                proposed_risk_percent=proposed_risk_percent,
                total_risk_percent=total_risk_percent,
            )

        # -----------------------------------------------------
        # Maximum portfolio risk
        # -----------------------------------------------------

        if total_risk_value > self.max_risk_value:
            return PortfolioRiskAssessment(
                permitted=False,
                reason=(
                    "Maximum portfolio risk would "
                    "be exceeded."
                ),
                current_open_trades=current_open_trades,
                current_risk_value=current_risk_value,
                proposed_risk_value=proposed_risk_value,
                total_risk_value=total_risk_value,
                current_risk_percent=current_risk_percent,
                proposed_risk_percent=proposed_risk_percent,
                total_risk_percent=total_risk_percent,
            )

        return PortfolioRiskAssessment(
            permitted=True,
            reason="Trade permitted under portfolio risk rules.",
            current_open_trades=current_open_trades,
            current_risk_value=current_risk_value,
            proposed_risk_value=proposed_risk_value,
            total_risk_value=total_risk_value,
            current_risk_percent=current_risk_percent,
            proposed_risk_percent=proposed_risk_percent,
            total_risk_percent=total_risk_percent,
        )