"""
===========================================================
TradePilotAI
Approval Manager
===========================================================

Stores pending trade approvals.
"""

from __future__ import annotations



class ApprovalManager:


    def __init__(self):

        self._pending = []



    def add(
        self,
        approval,
    ):

        self._pending.append(
            approval
        )



    def pending(self):

        return [

            trade

            for trade in self._pending

            if trade.is_pending

        ]



    def approve(
        self,
        symbol: str,
    ):

        for trade in self._pending:

            if trade.symbol == symbol:

                trade.approve()

                return trade


        return None



    def reject(
        self,
        symbol: str,
    ):

        for trade in self._pending:

            if trade.symbol == symbol:

                trade.reject()

                return trade


        return None