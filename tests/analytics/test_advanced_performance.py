"""
===========================================================
TradePilotAI
Advanced Performance Tests
===========================================================
"""

from analytics.performance_engine import PerformanceEngine



def test_profit_factor():

    engine = PerformanceEngine(

        [

            {"profit": 200},

            {"profit": -100},

        ]

    )


    assert engine.profit_factor == 2



def test_equity_curve():

    engine = PerformanceEngine(

        [

            {"profit": 100},

            {"profit": -50},

            {"profit": 200},

        ]

    )


    assert engine.equity_curve == [

        100,

        50,

        250,

    ]



def test_maximum_drawdown():

    engine = PerformanceEngine(

        [

            {"profit": 100},

            {"profit": 200},

            {"profit": -150},

        ]

    )


    assert engine.maximum_drawdown == 150