"""
===========================================================
TradePilotAI
Trade Journal

Records trading events.
===========================================================
"""

from __future__ import annotations

from datetime import datetime



class TradeJournal:
    """
    Stores trading events.
    """


    def __init__(self):

        self._events = []



    def record(
        self,
        event_type: str,
        symbol: str,
        details: dict | None = None,
    ) -> None:

        event = {

            "time": datetime.now(),

            "type": event_type,

            "symbol": symbol,

            "details": details or {},

        }


        self._events.append(
            event
        )



    def events(self):

        return self._events.copy()



    def count(self):

        return len(
            self._events
        )