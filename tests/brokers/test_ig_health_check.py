"""
===========================================================
TradePilotAI
IG Health Check Tests
===========================================================
"""

import pytest

from brokers.ig_health_check import IGHealthCheck



class FakeClient:

    def __init__(self, connected):

        self._connected = connected



def test_health_check_passes():

    client = FakeClient(
        True
    )


    health = IGHealthCheck(
        client
    )


    assert health.check()



def test_health_check_fails_when_disconnected():

    client = FakeClient(
        False
    )


    health = IGHealthCheck(
        client
    )


    with pytest.raises(ConnectionError):

        health.check()