"""
===========================================================
TradePilotAI
Live Trading Controller Tests
===========================================================
"""

import pandas as pd

from core.live_trading_controller import (
    LiveTradingController,
)



class FakeMarket:


    def get_latest_prices(
        self,
        symbol,
    ):

        return pd.DataFrame(

            [
                {
                    "Open":100,
                    "High":101,
                    "Low":99,
                    "Close":100,
                    "Volume":1000,
                },
                {
                    "Open":101,
                    "High":103,
                    "Low":100,
                    "Close":102,
                    "Volume":1200,
                },
            ]

        )



class FakeIndicators:


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



class FakePipeline:


    def process(
        self,
        signal,
    ):

        return signal



class FakeOrderFactory:


    def create_order(
        self,
        signal,
        quantity,
    ):

        return {
            "signal": signal,
            "quantity": quantity,
        }



class FakeExecution:


    def execute(
        self,
        order,
    ):

        return {
            "status": "DRY_RUN",
            "order": order,
        }



def test_controller_runs_complete_cycle():

    controller = LiveTradingController(

        FakeMarket(),

        FakeIndicators(),

        FakeStrategy(),

        FakePipeline(),

        FakeOrderFactory(),

        FakeExecution(),

    )


    result = controller.process(
        "RR.L"
    )


    assert result["status"] == "DRY_RUN"

    assert result["order"]["signal"] == "BUY"