"""
===========================================================
TradePilotAI
Optimisation Report Tests
===========================================================
"""

from optimisation.optimisation_report import (
    OptimisationReport,
)

from optimisation.optimisation_result import (
    OptimisationResult,
)



def create_result(
    score_type: int,
):
    """
    Create test optimisation results.
    """

    if score_type == 1:

        return OptimisationResult(

            parameters={
                "buy_rsi": 30
            },

            net_profit=10000,

            win_rate=60,

            profit_factor=2,

            max_drawdown=10,

            expectancy=50,

            total_trades=20,
        )


    return OptimisationResult(

        parameters={
            "buy_rsi": 25
        },

        net_profit=5000,

        win_rate=50,

        profit_factor=1,

        max_drawdown=20,

        expectancy=20,

        total_trades=10,
    )



def test_empty_report_returns_message():

    report = OptimisationReport([])


    assert report.best_result is None


    assert (
        report.to_text()
        ==
        "No optimisation results available."
    )



def test_results_are_ranked_by_score():

    results = [

        create_result(2),

        create_result(1),

    ]


    report = OptimisationReport(
        results
    )


    ranked = report.ranked_results


    assert (
        ranked[0].parameters["buy_rsi"]
        ==
        30
    )



def test_best_result_returns_highest_score():

    report = OptimisationReport(

        [
            create_result(2),

            create_result(1),

        ]

    )


    best = report.best_result


    assert (
        best.parameters["buy_rsi"]
        ==
        30
    )



def test_top_returns_requested_number():

    report = OptimisationReport(

        [
            create_result(1),

            create_result(2),

        ]

    )


    results = report.top(1)


    assert len(results) == 1



def test_report_text_contains_heading():

    report = OptimisationReport(

        [
            create_result(1)
        ]

    )


    text = report.to_text()


    assert (
        "TradePilotAI Optimisation Report"
        in text
    )