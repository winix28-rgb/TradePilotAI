"""
===========================================================
TradePilotAI
Order Factory
===========================================================

Creates executable TradeOrder objects from TradeSignal objects.
"""

from __future__ import annotations

from models.trade_order import TradeOrder
from signals.trade_signal import TradeSignal


class OrderFactory:
    """
    Converts strategy signals into executable orders.
    """

    def create_order(
        self,
        signal: TradeSignal,
        quantity: int,
    ) -> TradeOrder:
        """
        Create a TradeOrder from a TradeSignal.
        """

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero."
            )

        return TradeOrder(
            symbol=signal.symbol,
            action=signal.action,
            quantity=quantity,
            price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
        )