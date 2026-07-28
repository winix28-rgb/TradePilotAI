"""
===========================================================
TradePilotAI
Dashboard State

Central state container for the Streamlit application.
===========================================================
"""

from __future__ import annotations


from core.application_factory import ApplicationFactory
from dashboard.controller import DashboardController



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

        class SignalBridge:
            pass


        class OrderFactory:
            pass


        class ExecutionRouter:
            pass



        services = ApplicationFactory.create(

            SignalBridge(),

            OrderFactory(),

            ExecutionRouter(),

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


        # Dashboard control layer

        self.controller = DashboardController(
            self.application
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