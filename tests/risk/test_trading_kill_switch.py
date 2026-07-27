"""
===========================================================
TradePilotAI
Trading Kill Switch Tests
===========================================================
"""

from risk.trading_kill_switch import TradingKillSwitch



def test_trading_enabled_by_default():

    switch = TradingKillSwitch()

    assert switch.trading_allowed()



def test_activate_blocks_trading():

    switch = TradingKillSwitch()

    switch.activate()

    assert not switch.trading_allowed()



def test_deactivate_allows_trading():

    switch = TradingKillSwitch()

    switch.activate()

    switch.deactivate()

    assert switch.trading_allowed()