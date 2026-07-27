"""
===========================================================
TradePilotAI
Market Data Service Tests
===========================================================
"""

import pytest

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData

from data.data_provider import DataProvider
from data.market_data_service import (
    MarketDataService,
)


class FakeProvider(DataProvider):
    """
    Fake provider for testing.
    """

    def __init__(self):

        self.called = False


    def load(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> HistoricalData:

        self.called = True


        return HistoricalData(

            [

                Candle(

                    timestamp=None,

                    open=100,

                    high=105,

                    low=95,

                    close=102,

                    volume=1000,

                )

            ]

        )



def test_unknown_provider_raises_error():

    service = MarketDataService()


    with pytest.raises(ValueError):

        service.get_history(

            provider="unknown",

            symbol="TEST",

        )



def test_provider_can_be_registered():

    service = MarketDataService()


    provider = FakeProvider()


    service.register_provider(

        "fake",

        provider,

    )


    result = service.get_history(

        provider="fake",

        symbol="TEST",

    )


    assert provider.called is True


    assert isinstance(

        result,

        HistoricalData,

    )



def test_yahoo_provider_is_registered():

    service = MarketDataService()


    assert "yahoo" in service._providers



def test_csv_provider_is_registered():

    service = MarketDataService()


    assert "csv" in service._providers