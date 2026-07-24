"""
===========================================================
TradePilotAI
Pytest Fixtures
===========================================================
"""

import pytest

from brokers.paper_broker import PaperBroker
from portfolio.simulation_account import SimulationAccount


@pytest.fixture
def account():
    """
    Fresh simulation account for every test.
    """
    return SimulationAccount(100000)


@pytest.fixture
def broker(account):
    """
    Fresh paper broker.
    """
    return PaperBroker(account)