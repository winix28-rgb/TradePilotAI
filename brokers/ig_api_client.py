"""
===========================================================
TradePilotAI
IG API Client
===========================================================

Real IG Markets API implementation using trading-ig.
"""

from __future__ import annotations


from trading_ig import IGService

from brokers.ig_client import IGClient



class IGAPIClient(IGClient):
    """
    Concrete IG Markets API client.
    """


    def __init__(
        self,
        username: str,
        password: str,
        api_key: str,
        account_type: str = "DEMO",
    ) -> None:


        self._ig = IGService(

            username=username,

            password=password,

            api_key=api_key,

            acc_type=account_type,

        )


        self._connected = False



    # =====================================================
    # CONNECTION
    # =====================================================

    def connect(self) -> None:

        if not self._connected:

            self._ig.create_session()

            self._connected = True



    # =====================================================
    # ACCOUNT
    # =====================================================

    def get_account_summary(self) -> dict:

        self.connect()

        return self._ig.fetch_accounts()



    # =====================================================
    # HISTORICAL DATA
    # =====================================================

    def get_historical_prices(
        self,
        epic: str,
        start_date: str,
        end_date: str,
    ):

        self.connect()


        response = (
            self._ig.fetch_historical_prices_by_epic(

                epic,

                resolution="DAY",

                start_date=start_date,

                end_date=end_date,

            )
        )


        prices = []


        for candle in response["prices"]:

            prices.append(

                {
                    "timestamp":
                        candle.name.isoformat(),

                    "open":
                        candle["openPrice"]["ask"],

                    "high":
                        candle["highPrice"]["ask"],

                    "low":
                        candle["lowPrice"]["ask"],

                    "close":
                        candle["closePrice"]["ask"],

                    "volume":
                        candle["lastTradedVolume"],

                }

            )


        return prices



    # =====================================================
    # MARKET DATA
    # =====================================================

    def get_market_prices(
        self,
        epic: str,
        resolution="DAY",
    ):

        self.connect()


        response = (
            self._ig.fetch_historical_prices_by_epic(

                epic,

                resolution=resolution,

            )
        )


        return response["prices"]



    # =====================================================
    # TRADING
    # =====================================================

    def open_position(
        self,
        epic: str,
        direction: str,
        size: float,
        order_type: str = "MARKET",
    ):

        self.connect()


        return self._ig.create_open_position(

            epic=epic,

            expiry="-",

            direction=direction,

            size=size,

            order_type=order_type,

        )



    def close_position(
        self,
        deal_id: str,
    ):

        self.connect()


        return self._ig.close_open_position(

            deal_id=deal_id,

        )