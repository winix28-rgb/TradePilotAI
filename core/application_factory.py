"""
===========================================================
TradePilotAI
Application Factory
===========================================================

Creates and wires the complete trading application.
"""

from __future__ import annotations


from core.approval_manager import ApprovalManager
from core.trade_journal import TradeJournal
from analytics.performance_engine import PerformanceEngine



class ApplicationFactory:
    """
    Builds the TradePilotAI application stack.
    """



    @staticmethod
    def create(
        signal_bridge,
        order_factory,
        execution_router,
    ):
        """
        Create fully connected application.
        """


        approval_manager = ApprovalManager()

        journal = TradeJournal()

        performance = PerformanceEngine()



        from core.trading_application import (
            TradingApplication,
        )


        application = TradingApplication(

            signal_bridge,

            approval_manager,

            order_factory,

            execution_router,

            journal,

        )


        return {

            "application": application,

            "approval_manager": approval_manager,

            "journal": journal,

            "performance": performance,

        }