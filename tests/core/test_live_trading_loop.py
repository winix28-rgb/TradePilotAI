"""
===========================================================
TradePilotAI
Live Trading Loop Tests
===========================================================
"""

import pandas as pd

from core.live_trading_loop import LiveTradingLoop



class FakeMarketService:


    def get_latest_prices(
        self,
        symbol,
    ):

        return pd.DataFrame(

            [
                {
                    "Open":100,
                    "High":105,
                    "Low":99,
                    "Close":103,
                    "Volume":1000,
                },

                {
                    "Open":103,
                    "High":107,
                    "Low":102,
                    "Close":106,
                    "Volume":1200,
                }

            ]

        )



class FakeIndicatorEngine:


    def add_indicators(
        self,
        data,
    ):

        return data



class FakeStrategy:


    def on_bar(
        self,
        previous,
        current,
    ):

        return "BUY"



def test_live_loop_process_cycle():

    loop = LiveTradingLoop(

        market_service=FakeMarketService(),

        indicator_engine=FakeIndicatorEngine(),

        strategy=FakeStrategy(),

    )


    result = loop.process_cycle(
        "RR.L"
    )


    assert result == "BUY"