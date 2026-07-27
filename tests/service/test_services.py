"""
===========================================================
TradePilotAI
Service Tests
===========================================================
"""

from services.account_service import AccountService
from services.market_data_service import MarketDataService



class FakeClient:


    def get_account_summary(self):

        return {
            "balance": 10000
        }



class FakeMarketProvider:


    def get_historical_prices(
        self,
        symbol,
        start_date,
        end_date,
    ):

        return [
            {
                "symbol": symbol
            }
        ]



def test_account_service():

    service = AccountService(
        FakeClient()
    )


    result = service.get_account_summary()


    assert result["balance"] == 10000



def test_market_data_service():

    service = MarketDataService(
        FakeMarketProvider()
    )


    result = service.get_prices(

        "RR.L",

        "2025-01-01",

        "2025-12-31",

    )


    assert result[0]["symbol"] == "RR.L"