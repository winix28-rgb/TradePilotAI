"""
===========================================================
TradePilotAI
Trade Engine Risk Gateway Tests
===========================================================
"""

import pytest

from brokers.paper_broker import PaperBroker

from core.trade_engine import TradeEngine
from core.risk_gateway import RiskGateway

from models.trade_order import TradeOrder

from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount

from risk.daily_loss_limit import DailyLossLimit
from risk.max_position_manager import MaxPositionManager
from risk.trading_kill_switch import TradingKillSwitch
from risk.position_reconciler import PositionReconciler

from signals.signal_types import SignalType



def create_engine():

    account = SimulationAccount(
        10000
    )

    portfolio = PortfolioManager(
        account
    )

    broker = PaperBroker(
        account
    )


    gateway = RiskGateway(

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


    engine = TradeEngine(

        broker,

        portfolio,

        gateway,

    )


    return engine, gateway, portfolio



def create_buy_order():

    return TradeOrder(

        symbol="RR.L",

        action=SignalType.BUY,

        quantity=10,

        price=100,

        stop_loss=95,

        take_profit=110,

        strategy="RSI",

    )



def test_trade_passes_risk_gateway():

    engine, _, portfolio = create_engine()


    result = engine.execute(
        create_buy_order()
    )


    assert result.symbol == "RR.L"

    assert (
        portfolio.get_position("RR.L")
        is not None
    )



def test_kill_switch_blocks_trade():

    engine, gateway, _ = create_engine()


    gateway._kill_switch.activate()


    with pytest.raises(PermissionError):

        engine.execute(
            create_buy_order()
        )



def test_daily_loss_blocks_trade():

    engine, _, portfolio = create_engine()


    portfolio.account.withdraw(
        300
    )


    with pytest.raises(PermissionError):

        engine.execute(
            create_buy_order()
        )



def test_max_position_limit_blocks_trade():

    engine, _, portfolio = create_engine()


    for symbol in [
        "AAA",
        "BBB",
        "CCC",
        "DDD",
        "EEE",
    ]:

        portfolio.add_position(

            create_position(
                symbol
            )

        )


    with pytest.raises(PermissionError):

        engine.execute(
            create_buy_order()
        )



def create_position(symbol):

    from models.position import Position

    return Position(

        symbol=symbol,

        quantity=1,

        entry_price=100,

        current_price=100,

        stop_loss=95,

        take_profit=110,

        strategy="TEST",

    )