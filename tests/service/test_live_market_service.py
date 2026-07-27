"""
===========================================================
TradePilotAI
Live Market Service Tests
===========================================================
"""

from services.live_market_service import LiveMarketService



class FakeIGClient:


    def get_market_prices(
        self,
        epic,
        resolution,
    ):

        class FakeDate:

            def __hash__(self):
                return 1


        class Candle(dict):

            name = FakeDate()


        return [

            Candle(
                {
                    "openPrice":
                        {
                            "ask":100
                        },

                    "highPrice":
                        {
                            "ask":105
                        },

                    "lowPrice":
                        {
                            "ask":98
                        },

                    "closePrice":
                        {
                            "ask":103
                        },

                    "lastTradedVolume":
                        1000,
                }
            )

        ]



def test_live_market_service_returns_dataframe():

    service = LiveMarketService(
        FakeIGClient()
    )


    data = service.get_latest_prices(
        "RR.L"
    )


    assert len(data) == 1

    assert data.iloc[0]["Close"] == 103