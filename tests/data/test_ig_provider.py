"""
===========================================================
TradePilotAI
IG Provider Tests
===========================================================
"""

from datetime import datetime

from backtesting.historical_data import HistoricalData

from data.ig_provider import IGProvider



class FakeIGClient:
    """
    Fake IG client for testing.
    """

    def __init__(self):

        self.called = False


    def get_historical_prices(
        self,
        epic: str,
        start_date: str,
        end_date: str,
    ):

        self.called = True


        return [

            {
                "timestamp": "2025-01-01T10:00:00",

                "open": 100,

                "high": 105,

                "low": 95,

                "close": 102,

                "volume": 1000,
            },

            {
                "timestamp": "2025-01-02T10:00:00",

                "open": 102,

                "high": 108,

                "low": 101,

                "close": 107,

            },

        ]



def test_ig_provider_returns_historical_data():

    client = FakeIGClient()


    provider = IGProvider(
        client
    )


    result = provider.load(
        symbol="RR.L"
    )


    assert isinstance(
        result,
        HistoricalData,
    )


    assert len(result) == 2



def test_ig_client_is_called():

    client = FakeIGClient()


    provider = IGProvider(
        client
    )


    provider.load(
        symbol="RR.L"
    )


    assert client.called is True



def test_candle_values_are_converted():

    client = FakeIGClient()


    provider = IGProvider(
        client
    )


    history = provider.load(
        symbol="RR.L"
    )


    candle = history[0]


    assert candle.open == 100

    assert candle.high == 105

    assert candle.low == 95

    assert candle.close == 102



def test_missing_volume_defaults_to_zero():

    client = FakeIGClient()


    provider = IGProvider(
        client
    )


    history = provider.load(
        symbol="RR.L"
    )


    candle = history[1]


    assert candle.volume == 0