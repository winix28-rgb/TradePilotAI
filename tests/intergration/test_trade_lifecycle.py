"""
===========================================================
TradePilotAI
Integration Test
Trade History
===========================================================
"""

from brokers.paper_broker import PaperBroker
from core.trade_engine import TradeEngine
from models.trade import Trade
from models.trade_order import TradeOrder
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount
from signals.signal_types import SignalType


def test_completed_trade_is_added_to_trade_history():

    account = SimulationAccount(10000)

    portfolio = PortfolioManager(account)

    broker = PaperBroker(account)

    engine = TradeEngine(broker, portfolio)

    buy_order = TradeOrder(
        symbol="AAPL",
        action=SignalType.BUY,
        quantity=10,
        price=100,
        stop_loss=95,
        take_profit=120,
        strategy="Test Strategy",
    )

    engine.execute(buy_order)

    sell_order = TradeOrder(
        symbol="AAPL",
        action=SignalType.SELL,
        quantity=10,
        price=110,
        stop_loss=95,
        take_profit=120,
        strategy="Test Strategy",
    )

    trade = engine.execute(sell_order)

    assert isinstance(trade, Trade)

    assert len(portfolio.trade_history) == 1

    assert portfolio.trade_history[0] == trade

    assert not portfolio.has_position("AAPL")