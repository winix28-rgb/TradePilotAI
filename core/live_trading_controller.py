"""
===========================================================
TradePilotAI
Live Trading Controller
===========================================================

Coordinates the complete trading decision workflow.

Version 1:
- Market data
- Strategy
- Risk approval
- Order creation
- Execution routing

Supports DRY_RUN mode.
"""

from __future__ import annotations



class LiveTradingController:
    """
    Coordinates live trading decisions.
    """


    def __init__(
        self,
        market_service,
        indicator_engine,
        strategy,
        signal_pipeline,
        order_factory,
        execution_router,
    ) -> None:

        self.market_service = market_service

        self.indicator_engine = indicator_engine

        self.strategy = strategy

        self.signal_pipeline = signal_pipeline

        self.order_factory = order_factory

        self.execution_router = execution_router



    def process(
        self,
        symbol: str,
        quantity: int = 1,
    ):
        """
        Run one complete trading cycle.
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


        approved = (
            self.signal_pipeline.process(
                signal
            )
        )


        if approved is None:

            return None



        order = (
            self.order_factory.create_order(
                approved,
                quantity,
            )
        )


        result = (
            self.execution_router.execute(
                order
            )
        )


        return result