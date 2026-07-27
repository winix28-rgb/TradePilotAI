"""
===========================================================
TradePilotAI
Risk Gateway Tests
===========================================================
"""

from risk.daily_loss_limit import DailyLossLimit
from risk.max_position_manager import MaxPositionManager
from risk.trading_kill_switch import TradingKillSwitch
from risk.position_reconciler import PositionReconciler

from core.risk_gateway import RiskGateway



def create_gateway():

    return RiskGateway(

        daily_loss_limit=DailyLossLimit(
            starting_balance=10000,
            max_loss_percent=2,
        ),

        max_position_manager=MaxPositionManager(
            maximum_positions=5,
        ),

        kill_switch=TradingKillSwitch(),

        position_reconciler=PositionReconciler(),

    )



def test_trade_is_approved():

    gateway = create_gateway()


    approved, reason = gateway.approve_trade(

        current_balance=10000,

        current_positions=2,

    )


    assert approved

    assert reason == "Approved"



def test_kill_switch_blocks_trade():

    gateway = create_gateway()


    gateway._kill_switch.activate()


    approved, _ = gateway.approve_trade(

        current_balance=10000,

        current_positions=1,

    )


    assert not approved



def test_daily_loss_blocks_trade():

    gateway = create_gateway()


    approved, _ = gateway.approve_trade(

        current_balance=9700,

        current_positions=1,

    )


    assert not approved



def test_position_limit_blocks_trade():

    gateway = create_gateway()


    approved, _ = gateway.approve_trade(

        current_balance=10000,

        current_positions=5,

    )


    assert not approved