"""
===========================================================
TradePilotAI
Live Trading Loop
===========================================================

Runs the live market evaluation cycle.

Version 1:
- Reads market data
- Calculates indicators
- Generates signals
- Does NOT execute trades
"""

from __future__ import annotations

import time



class LiveTradingLoop:
    """
    Controls the live trading cycle.
    """


    def __init__(
        self,
        market_service,
        indicator_engine,
        strategy,
        interval_seconds: int = 60,
    ) -> None:

        self.market_service = market_service

        self.indicator_engine = indicator_engine

        self.strategy = strategy

        self.interval_seconds = interval_seconds

        self.running = False



    def start(
        self,
        symbol: str,
    ) -> None:
        """
        Start live evaluation.
        """

        self.running = True


        while self.running:

            self.process_cycle(
                symbol
            )


            time.sleep(
                self.interval_seconds
            )



    def stop(self) -> None:
        """
        Stop loop.
        """

        self.running = False



    def process_cycle(
        self,
        symbol: str,
    ):
        """
        Execute one market evaluation cycle.
        """


        data = (
            self.market_service.get_latest_prices(
                symbol
            )
        )


        if data.empty:

            return None


        data = (
            self.indicator_engine.add_indicators(
                data
            )
        )


        previous = data.iloc[-2]

        current = data.iloc[-1]


        signal = (
            self.strategy.on_bar(
                previous,
                current,
            )
        )


        return signal