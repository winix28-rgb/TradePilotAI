"""
===========================================================
TradePilotAI
Optimisation Backtest Adapter
===========================================================

Connects the optimisation engine to the normal backtesting
pipeline.

Allows Optimiser to supply different StrategyConfig values
while keeping the normal BacktestRunner architecture.
"""

from __future__ import annotations

from backtesting.historical_data import HistoricalData

from models.application_config import ApplicationConfig
from models.strategy_config import StrategyConfig

from strategies.rsi_mean_reversion import (
    RSIMeanReversionStrategy,
)


class OptimisationBacktestRunner:
    """
    Adapter used by the Optimiser.

    The optimiser supplies a StrategyConfig.
    The adapter creates the strategy and executes a
    normal backtest.
    """

    def __init__(
        self,
        base_config: ApplicationConfig,
        symbol: str,
        historical_data: HistoricalData,
        backtest_runner_factory,
    ) -> None:

        self._base_config = base_config

        self._symbol = symbol

        self._historical_data = historical_data

        self._backtest_runner_factory = (
            backtest_runner_factory
        )


    def run(
        self,
        strategy_config: StrategyConfig,
    ):

        strategy = RSIMeanReversionStrategy(
            strategy_config
        )


        runner = self._backtest_runner_factory(
            self._base_config
        )


        return runner.run_with_strategy(

            symbol=self._symbol,

            strategy=strategy,

            historical_data=self._historical_data,
        )