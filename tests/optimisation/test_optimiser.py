"""
===========================================================
TradePilotAI
Optimiser Tests
===========================================================
"""

from optimisation.optimiser import Optimiser
from optimisation.parameter_grid import ParameterGrid

from optimisation.optimisation_result import (
    OptimisationResult,
)


class FakeTrade:
    """
    Fake trade object for testing.

    TradeAnalyser requires:
        trade.profit
    """

    def __init__(
        self,
        profit: float,
    ):

        self.profit = profit



class FakePortfolio:
    """
    Fake portfolio containing completed trades.
    """

    def __init__(self):

        self.trade_history = [

            FakeTrade(100),

            FakeTrade(-50),

            FakeTrade(200),

        ]



class FakeBacktestResult:
    """
    Minimal fake backtest result for testing.
    """

    def __init__(
        self,
        profit: float,
    ):

        self.net_profit = profit


        self.analytics = type(
            "Analytics",
            (),
            {
                "max_drawdown": 10
            }
        )()


        self.portfolio = FakePortfolio()



class FakeRunner:
    """
    Fake backtest runner.
    """

    def run(
        self,
        strategy,
    ):

        return FakeBacktestResult(
            profit=1000
        )



def fake_strategy_factory(
    config,
):

    return config



def test_optimiser_runs_parameter_sets():

    grid = ParameterGrid(

        {
            "buy_rsi": [25, 30],

            "exit_rsi": [50],

            "ema_fast": [12],

            "ema_slow": [26],
        }

    )


    optimiser = Optimiser(

        parameter_grid=grid,

        backtest_runner=FakeRunner(),

        strategy_factory=fake_strategy_factory,

    )


    results = optimiser.run()


    assert len(results) == 2


    assert isinstance(

        results[0],

        OptimisationResult,

    )



def test_best_result_returns_highest_score():

    optimiser = Optimiser(

        parameter_grid=ParameterGrid({}),

        backtest_runner=FakeRunner(),

        strategy_factory=fake_strategy_factory,

    )


    results = [

        OptimisationResult(

            parameters={
                "test": 1
            },

            net_profit=100,

            win_rate=50,

            profit_factor=1,

            max_drawdown=20,

            expectancy=10,

            total_trades=5,

        ),


        OptimisationResult(

            parameters={
                "test": 2
            },

            net_profit=200,

            win_rate=70,

            profit_factor=3,

            max_drawdown=10,

            expectancy=20,

            total_trades=10,

        ),

    ]


    best = optimiser.best_result(
        results
    )


    assert best.parameters["test"] == 2