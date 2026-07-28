"""
===========================================================
TradePilotAI
Demo Signal Service
===========================================================

Application service for creating demo trading signals
from the dashboard.
"""

from __future__ import annotations


from services.demo_signal_generator import (
    DemoSignalGenerator,
)



class DemoSignalService:
    """
    Handles demo signal creation and submission.
    """



    def __init__(
        self,
        signal_bridge,
    ) -> None:

        self.signal_bridge = signal_bridge

        self.generator = DemoSignalGenerator()



    def create_demo_trade(
        self,
    ):
        """
        Create a demo trade and send it
        into the approval workflow.
        """


        signal = (
            self.generator.create_buy_signal()
        )


        return (
            self.signal_bridge.submit(
                signal
            )
        )