"""
===========================================================
TradePilotAI
Performance Engine Tests
===========================================================
"""

from analytics.performance_engine import (
    PerformanceEngine,
)



def test_total_trades():

    engine = PerformanceEngine(

        [

            {
                "profit": 100
            },

            {
                "profit": -50
            }

        ]

    )


    assert engine.total_trades == 2



def test_winning_trades():

    engine = PerformanceEngine(

        [

            {
                "profit": 100
            },

            {
                "profit": -50
            }

        ]

    )


    assert engine.winning_trades == 1



def test_win_rate():

    engine = PerformanceEngine(

        [

            {
                "profit": 100
            },

            {
                "profit": -50
            }

        ]

    )


    assert engine.win_rate == 50



def test_net_profit():

    engine = PerformanceEngine(

        [

            {
                "profit": 100
            },

            {
                "profit": -50
            }

        ]

    )


    assert engine.net_profit == 50