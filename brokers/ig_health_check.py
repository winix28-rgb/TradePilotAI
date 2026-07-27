"""
===========================================================
TradePilotAI
IG Health Check
===========================================================

Validates IG API availability before trading starts.
"""

from __future__ import annotations



class IGHealthCheck:
    """
    Performs IG connection validation.
    """


    def __init__(
        self,
        client,
    ) -> None:

        self._client = client



    def check(self) -> bool:
        """
        Return True if IG connection is healthy.
        """

        if not getattr(
            self._client,
            "_connected",
            False,
        ):

            raise ConnectionError(
                "IG client is not connected."
            )


        return True