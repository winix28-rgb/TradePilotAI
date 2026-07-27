"""
===========================================================
TradePilotAI
Trading Kill Switch
===========================================================

Emergency control to stop new trade execution.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TradingKillSwitch:
    """
    Controls whether trading is enabled.
    """

    enabled: bool = True


    def activate(self) -> None:
        """
        Disable trading.
        """

        self.enabled = False


    def deactivate(self) -> None:
        """
        Re-enable trading.
        """

        self.enabled = True


    def trading_allowed(self) -> bool:
        """
        Return current trading state.
        """

        return self.enabled