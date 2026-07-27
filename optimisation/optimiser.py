"""
===========================================================
TradePilotAI
Optimiser
===========================================================

Runs multiple strategy parameter combinations and returns
the best performing configuration.
"""

from __future__ import annotations

from analytics.performance_report import PerformanceReport

from models.strategy_config import StrategyConfig

from optimisation.optimisation_result import (
    OptimisationResult,
)

from optimisation.parameter_grid import ParameterGrid


class Optimiser:
    """
    Executes strategy optimisation.

    For each parameter combination:

        1. Create StrategyConfig
        2. Create strategy
        3. Run backtest
        4. Analyse performance
        5. Store result
    """

    def __init__(
        self,
        parameter_grid: ParameterGrid,
        backtest_runner,
        strategy_factory,
    ) -> None:

        self._parameter_grid = parameter_grid

        self._backtest_runner = backtest_runner

        self._strategy_factory = strategy_factory



    def run(self) -> list[OptimisationResult]:
        """
        Run every parameter combination.

        Returns:
            List of optimisation results.
        """

        results = []


        for parameters in self._parameter_grid.generate():


            config = StrategyConfig(
                **parameters
            )


            strategy = self._strategy_factory(
                config
            )


            backtest_result = (
                self._backtest_runner.run(
                    strategy
                )
            )


            report = PerformanceReport(
                backtest_result
            )


            result = OptimisationResult(

                parameters=parameters,

                net_profit=(
                    backtest_result.net_profit
                ),

                win_rate=(
                    report.win_rate
                ),

                profit_factor=(
                    report.profit_factor
                ),

                max_drawdown=(
                    backtest_result.analytics
                    .max_drawdown
                ),

                expectancy=(
                    report.expectancy
                ),

                total_trades=(
                    len(
                        backtest_result
                        .portfolio
                        .trade_history
                    )
                ),
            )


            results.append(
                result
            )


        return results



    def best_result(
        self,
        results: list[OptimisationResult],
    ) -> OptimisationResult | None:
        """
        Return highest scoring result.
        """

        if not results:

            return None


        return max(
            results,
            key=lambda result: result.score,
        )