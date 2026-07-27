"""
===========================================================
TradePilotAI
Signal Pipeline Tests
===========================================================
"""

from core.signal_pipeline import SignalPipeline



class ApprovingRiskGateway:


    def approve(
        self,
        signal,
    ):

        return True



class RejectingRiskGateway:


    def approve(
        self,
        signal,
    ):

        return False



def test_signal_passes_risk():

    pipeline = SignalPipeline(
        ApprovingRiskGateway()
    )


    result = pipeline.process(
        "BUY"
    )


    assert result == "BUY"



def test_signal_rejected():

    pipeline = SignalPipeline(
        RejectingRiskGateway()
    )


    result = pipeline.process(
        "BUY"
    )


    assert result is None



def test_empty_signal():

    pipeline = SignalPipeline(
        ApprovingRiskGateway()
    )


    result = pipeline.process(
        None
    )


    assert result is None