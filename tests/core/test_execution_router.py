"""
===========================================================
TradePilotAI
Execution Router Tests
===========================================================
"""

from core.execution_router import ExecutionRouter



class FakeBroker:


    def execute(
        self,
        order,
    ):

        return {
            "status": "EXECUTED",
            "order": order,
        }



def test_dry_run_does_not_execute():

    router = ExecutionRouter(
        FakeBroker(),
        "DRY_RUN",
    )


    result = router.execute(
        "BUY RR.L"
    )


    assert result["status"] == "DRY_RUN"



def test_demo_routes_to_broker():

    router = ExecutionRouter(
        FakeBroker(),
        "DEMO",
    )


    result = router.execute(
        "BUY RR.L"
    )


    assert result["status"] == "EXECUTED"



def test_invalid_mode():

    router = ExecutionRouter(
        FakeBroker(),
        "UNKNOWN",
    )


    try:

        router.execute(
            "BUY"
        )

        assert False

    except ValueError:

        assert True