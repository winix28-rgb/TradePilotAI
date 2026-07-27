"""
===========================================================
TradePilotAI
Full Risk Pipeline Integration Tests
===========================================================
"""

from datetime import datetime

from brokers.paper_broker import PaperBroker

from core.trade_engine import TradeEngine

from models.risk_config import RiskConfig
from models.trade_order import TradeOrder

from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount

from signals.signal_types import SignalType



def create_trade_engine():

    account = SimulationAccount(
        100000
    )

    portfolio = PortfolioManager(
        account
    )

    broker = PaperBroker(
        account
    )

    return TradeEngine(
        broker,
        portfolio,
    )



def test_risk_sized_order_creates_position():

    engine = create_trade_engine()


    config = RiskConfig(
        risk_per_trade=1.0
    )


    portfolio_value = (
        engine.portfolio.total_value
    )


    maximum_risk = (
        portfolio_value
        *
        (
            config.risk_per_trade
            /
            100
        )
    )


    entry_price = 100

    stop_price = 95


    risk_per_share = (
        entry_price
        -
        stop_price
    )


    quantity = int(
        maximum_risk
        /
        risk_per_share
    )


    order = TradeOrder(

        symbol="RR.L",

        action=SignalType.BUY,

        quantity=quantity,

        price=entry_price,

        stop_loss=stop_price,

        timestamp=datetime.now(),
    )


    position = engine.execute(
        order
    )


    assert position.symbol == "RR.L"

    assert position.quantity == 200


    assert (
        engine.portfolio.has_position("RR.L")
        is True
    )