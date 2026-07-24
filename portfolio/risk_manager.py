"""
===========================================================
TradePilotAI
Risk Manager
===========================================================

Responsible for validating TradeOrder objects before they
are submitted to a broker for execution.

The RiskManager enforces portfolio-level business rules,
ensuring that only valid and permitted orders progress to
the execution layer.

Author: TradePilotAI
Python: 3.12
"""

from __future__ import annotations

from models.trade_order import TradeOrder
from portfolio.portfolio_manager import PortfolioManager


class RiskManager:
    """
    Validates TradeOrder instances against portfolio rules.

    The RiskManager does not execute trades or calculate
    position sizes. Its sole responsibility is determining
    whether an order is permitted.
    """

    def __init__(self, portfolio: PortfolioManager) -> None:
        """
        Initialise the RiskManager.

        Args:
            portfolio:
                The portfolio against which all validation
                rules will be evaluated.
        """
        self._portfolio = portfolio

    def validate(self, order: TradeOrder) -> tuple[bool, str]:
        """
        Validate a proposed trade order.

        Validation Rules
        ----------------
        1. Quantity must be greater than zero.
        2. Price must be greater than zero.
        3. Portfolio must not already contain the symbol.
        4. Order value must not exceed available buying power.

        Args:
            order:
                The TradeOrder to validate.

        Returns:
            tuple[bool, str]

            True, "Approved"
                The order passed all validation rules.

            False, "<reason>"
                The order failed validation.
        """

        if order.quantity <= 0:
            return False, "Quantity must be greater than zero."

        if order.price <= 0:
            return False, "Price must be greater than zero."

        if self._portfolio.has_position(order.symbol):
            return (
                False,
                f"Portfolio already contains position '{order.symbol}'.",
            )

        if order.value > self._portfolio.account.buying_power:
            return (
                False,
                "Insufficient buying power for this order.",
            )

        return True, "Approved"
