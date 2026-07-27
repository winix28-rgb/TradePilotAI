"""
===========================================================
TradePilotAI
Broker Factory
===========================================================

Creates the correct broker implementation based on runtime
configuration.
"""

from __future__ import annotations


from brokers.broker import Broker

from brokers.paper_broker import PaperBroker
from brokers.ig_broker import IGBroker

from brokers.ig_api_client import IGAPIClient
from brokers.ig_connection import IGConnectionManager

from config.settings import Settings

from portfolio.simulation_account import SimulationAccount



class BrokerFactory:
    """
    Creates broker implementations.
    """


    @staticmethod
    def create(
        settings: Settings,
        account: SimulationAccount,
    ) -> Broker:
        """
        Create broker from runtime settings.
        """


        mode = settings.mode.upper()


        # ----------------------------------------------
        # PAPER
        # ----------------------------------------------

        if mode == "PAPER":

            return PaperBroker(
                account
            )


        # ----------------------------------------------
        # IG DEMO
        # ----------------------------------------------

        if mode == "DEMO":


            if not settings.ig_username:

                raise ValueError(
                    "IG_USERNAME is required for DEMO mode."
                )


            if not settings.ig_password:

                raise ValueError(
                    "IG_PASSWORD is required for DEMO mode."
                )


            if not settings.ig_api_key:

                raise ValueError(
                    "IG_API_KEY is required for DEMO mode."
                )


            client = IGAPIClient(

                username=settings.ig_username,

                password=settings.ig_password,

                api_key=settings.ig_api_key,

                account_type=settings.ig_account_type,

            )


            connection = IGConnectionManager(
                client
            )


            connection.connect()


            return IGBroker(
                client
            )


        raise ValueError(
            f"Unsupported broker mode: {settings.mode}"
        )