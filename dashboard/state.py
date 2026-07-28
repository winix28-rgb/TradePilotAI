"""
===========================================================
TradePilotAI
Dashboard State
===========================================================

Shared dashboard application state.
"""

from __future__ import annotations

from core.approval_manager import ApprovalManager


class DashboardState:
    """
    Stores dashboard runtime state.
    """


    def __init__(self):

        self.approval_manager = ApprovalManager()

        self.mode = "DEMO"

        self.engine_status = "RUNNING"

        self.connection_status = "CONNECTED"



    def pending_trades(self):

        return self.approval_manager.pending()



# Global dashboard state

state = DashboardState()