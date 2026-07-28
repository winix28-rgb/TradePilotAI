"""
===========================================================
TradePilotAI
Demo Signal Generator Tests
===========================================================
"""

from services.demo_signal_generator import (
    DemoSignalGenerator,
)



def test_demo_signal_creation():

    generator = DemoSignalGenerator()


    signal = (
        generator.create_buy_signal()
    )


    assert signal.symbol == "RR.L"

    assert signal.action == "BUY"

    assert signal.entry_price == 8.50

    assert signal.stop_loss == 8.20

    assert signal.strategy == "RSI Mean Reversion"