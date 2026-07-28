"""
===========================================================
TradePilotAI
Demo Signal Generator
===========================================================

Creates controlled test signals for dashboard workflow
validation.
"""

from __future__ import annotations



class DemoSignal:
    """
    Simple trading signal object.
    """

    def __init__(
        self,
        symbol: str,
        action: str,
        entry_price: float,
        stop_loss: float,
        strategy: str,
    ):

        self.symbol = symbol

        self.action = action

        self.entry_price = entry_price

        self.stop_loss = stop_loss

        self.strategy = strategy



class DemoSignalGenerator:
    """
    Generates safe test trading signals.
    """



    def create_buy_signal(self):

        return DemoSignal(

            symbol="RR.L",

            action="BUY",

            entry_price=8.50,

            stop_loss=8.20,

            strategy="RSI Mean Reversion",

        )