"""
===========================================================
TradePilotAI
IG Connection Manager Tests
===========================================================
"""

from brokers.ig_connection import IGConnectionManager



class FakeIGClient:
    """
    Fake IG client.
    """


    def __init__(self):

        self.connected = False



    def connect(self):

        self.connected = True



def test_connection_starts_disconnected():

    client = FakeIGClient()

    manager = IGConnectionManager(
        client
    )


    assert not manager.connected



def test_connection_connects():

    client = FakeIGClient()

    manager = IGConnectionManager(
        client
    )


    manager.connect()


    assert manager.connected

    assert client.connected



def test_disconnect():

    client = FakeIGClient()

    manager = IGConnectionManager(
        client
    )


    manager.connect()

    manager.disconnect()


    assert not manager.connected