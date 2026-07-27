"""
===========================================================
TradePilotAI
Broker Factory Tests
===========================================================
"""

import pytest

from brokers.broker_factory import BrokerFactory
from brokers.paper_broker import PaperBroker

from config.settings import Settings

from portfolio.simulation_account import SimulationAccount



def create_settings(mode):

    return Settings(

        mode=mode,

        ig_username="user",

        ig_password="password",

        ig_api_key="key",

        ig_account_type="DEMO",

    )



def test_factory_creates_paper_broker():

    account = SimulationAccount(
        10000
    )


    broker = BrokerFactory.create(

        create_settings(
            "PAPER"
        ),

        account,

    )


    assert isinstance(
        broker,
        PaperBroker,
    )



def test_demo_requires_credentials():

    account = SimulationAccount(
        10000
    )


    settings = Settings(

        mode="DEMO",

        ig_username=None,

        ig_password=None,

        ig_api_key=None,

        ig_account_type="DEMO",

    )


    with pytest.raises(ValueError):

        BrokerFactory.create(

            settings,

            account,

        )