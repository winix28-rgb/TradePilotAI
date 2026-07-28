"""
===========================================================
TradePilotAI
Performance Dashboard Tests
===========================================================
"""

from analytics.performance_engine import PerformanceEngine



def test_performance_metrics_available():

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

    assert engine.win_rate == 50

    assert engine.net_profit == 50