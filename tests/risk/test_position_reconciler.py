"""
===========================================================
TradePilotAI
Position Reconciler Tests
===========================================================
"""

from risk.position_reconciler import PositionReconciler



def test_matching_positions():

    reconciler = PositionReconciler()


    result = reconciler.reconcile(

        internal_positions=[
            "RR.L",
            "TSCO",
        ],

        broker_positions=[
            "RR.L",
            "TSCO",
        ],

    )


    assert result.matched



def test_missing_position_detected():

    reconciler = PositionReconciler()


    result = reconciler.reconcile(

        internal_positions=[
            "RR.L",
        ],

        broker_positions=[],

    )


    assert not result.matched

    assert "RR.L" in result.missing_positions



def test_unexpected_position_detected():

    reconciler = PositionReconciler()


    result = reconciler.reconcile(

        internal_positions=[],

        broker_positions=[
            "RR.L",
        ],

    )


    assert not result.matched

    assert "RR.L" in result.unexpected_positions