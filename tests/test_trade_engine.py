"""
===========================================================
TradePilotAI
Trade Engine Tests
===========================================================
"""

import pytest

from brokers.paper_broker import PaperBroker
from core.trade_engine import TradeEngine
from models.trade_order import TradeOrder
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount
from signals.signal_types import SignalType


@pytest.fixture
def account():
    return SimulationAccount(100000)


@pytest.fixture
def portfolio(account):
    return PortfolioManager(account)


@pytest.fixture
def broker(account):
    return PaperBroker(account)


@pytest.fixture
def engine(broker, portfolio):
    return TradeEngine(
        broker=broker,
        portfolio=portfolio,
    )


def test_execute_buy_order(engine):

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=100,
        price=250,
        stop_loss=240,
        take_profit=280,
        strategy="RSI",
    )

    position = engine.execute(order)

    assert position.symbol == "RR.L"
    assert position.quantity == 100

    assert engine.portfolio.has_position("RR.L")


def test_cash_is_reduced(engine):

    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=100,
        price=250,
    )

    engine.execute(order)

    assert engine.portfolio.account.cash == 75000


def test_execute_requires_trade_order(engine):

    with pytest.raises(TypeError):
        engine.execute(None)