"""
===========================================================
TradePilotAI
Application Factory Tests
===========================================================
"""

from core.application_factory import (
    ApplicationFactory,
)



class FakeBridge:
    pass



class FakeOrderFactory:
    pass



class FakeExecution:
    pass



def test_factory_creates_application():

    result = ApplicationFactory.create(

        FakeBridge(),

        FakeOrderFactory(),

        FakeExecution(),

    )


    assert "application" in result

    assert "journal" in result

    assert "performance" in result

    assert result["application"] is not None