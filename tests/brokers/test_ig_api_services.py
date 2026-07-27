"""
===========================================================
TradePilotAI
IG API Service Tests
===========================================================
"""

from brokers.ig_api_client import IGAPIClient



class FakeIGAPIClient(IGAPIClient):
    """
    Test client without connecting to IG.
    """


    def __init__(self):

        self._connected = True



    def get_account_summary(self):

        return {
            "balance": 10000
        }



    def get_market_prices(
        self,
        epic,
        resolution="DAY",
    ):

        return [
            {
                "epic": epic
            }
        ]



    def open_position(
        self,
        order,
    ):

        return {
            "dealReference": "TEST_OPEN"
        }



    def close_position(
        self,
        deal_id,
    ):

        return {
            "dealReference": "TEST_CLOSE"
        }



def test_account_summary():

    client = FakeIGAPIClient()


    result = client.get_account_summary()


    assert result["balance"] == 10000



def test_market_prices():

    client = FakeIGAPIClient()


    result = client.get_market_prices(
        "RR.L"
    )


    assert result[0]["epic"] == "RR.L"