"""
===========================================================
TradePilotAI
Dashboard State

Central state container for the Streamlit application.
===========================================================
"""

from __future__ import annotations


from core.application_factory import ApplicationFactory
from core.signal_bridge import SignalBridge

from dashboard.controller import DashboardController

from services.demo_signal_service import (
    DemoSignalService,
)



class DashboardState:
    """
    Holds the running TradePilotAI application state.
    """



    def __init__(self):

        self.engine_status = "RUNNING"

        self.mode = "DEMO"

        self.connection_status = "CONNECTED"


        self._build_application()



    def _build_application(self):

        """
        Create application services.
        """


        # Real SignalBridge

        signal_bridge = SignalBridge(
            None
        )


        class OrderFactory:
            pass


        class ExecutionRouter:
            pass



        services = ApplicationFactory.create(

            signal_bridge,

            OrderFactory(),

            ExecutionRouter(),

        )


        # Connect bridge to approval manager

        signal_bridge.approval_manager = (
            services["approval_manager"]
        )



        self.application = (
            services["application"]
        )


        self.approval_manager = (
            services["approval_manager"]
        )


        self.journal = (
            services["journal"]
        )


        self.performance = (
            services["performance"]
        )


        self.controller = DashboardController(
            self.application
        )


        self.demo_signal_service = DemoSignalService(

            signal_bridge

        )



    def pending_trades(self):

        """
        Return pending approval items.
        """

        return (
            self.controller.get_pending_trades()
        )



# Global dashboard state instance

state = DashboardState()