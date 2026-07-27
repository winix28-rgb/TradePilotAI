"""
===========================================================
TradePilotAI
Trading Session Tests
===========================================================
"""

import pytest

from brokers.paper_broker import PaperBroker

from core.trading_session import TradingSession

from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount

from core.risk_gateway import RiskGateway

from risk.daily_loss_limit import DailyLossLimit
from risk.max_position_manager import MaxPositionManager
from risk.trading_kill_switch import TradingKillSwitch
from risk.position_reconciler import PositionReconciler



def create_session():

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

        DailyLossLimit(
            10000
        ),

        MaxPositionManager(),

        TradingKillSwitch(),

        PositionReconciler(),

    )

    return TradingSession(
        broker,
        portfolio,
        gateway,
    )



def test_session_starts():

    session = create_session()

    session.start()

    assert session.running



def test_session_stops():

    session = create_session()

    session.start()

    session.stop()

    assert not session.running



def test_execute_without_start_fails():

    session = create_session()

    with pytest.raises(RuntimeError):

        session.execute_signal(None)