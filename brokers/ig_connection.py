"""
===========================================================
TradePilotAI
IG Connection Manager
===========================================================

Handles IG Markets connection lifecycle.
"""

from __future__ import annotations

from brokers.ig_api_client import IGAPIClient



class IGConnectionManager:
    """
    Controls IG API connection state.
    """


    def __init__(
        self,
        client: IGAPIClient,
    ) -> None:

        self._client = client

        self._connected = False



    @property
    def connected(self) -> bool:
        """
        Return connection status.
        """

        return self._connected



    def connect(self) -> None:
        """
        Establish IG session.
        """

        if self._connected:
            return


        self._client.connect()


        self._connected = True



    def disconnect(self) -> None:
        """
        Close connection state.
        """

        self._connected = False