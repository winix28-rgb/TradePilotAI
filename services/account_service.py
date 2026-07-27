"""
===========================================================
TradePilotAI
Account Service
===========================================================

Provides account information from supported brokers.
"""

from __future__ import annotations



class AccountService:
    """
    Retrieves broker account information.
    """


    def __init__(
        self,
        client,
    ) -> None:

        self._client = client



    def get_account_summary(self) -> dict:
        """
        Return account information.
        """

        if hasattr(
            self._client,
            "get_account_summary",
        ):

            return self._client.get_account_summary()


        raise NotImplementedError(
            "Broker client does not support account summary."
        )