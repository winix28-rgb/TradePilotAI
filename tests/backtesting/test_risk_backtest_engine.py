"""
===========================================================
TradePilotAI
Risk Backtest Engine Tests
===========================================================
"""

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData

from core.trade_engine import TradeEngine

from models.risk_config import RiskConfig
from models.trade_order import TradeOrder

from portfolio.portfolio_manager import PortfolioManager
from portfolio.risk_manager import RiskManager
from portfolio.simulation_account import SimulationAccount

from brokers.paper_broker import PaperBroker

from signals.signal_types import SignalType


def create_portfolio():

    account = SimulationAccount(
        100000
    )

    return PortfolioManager(
        account
    )


def create_candle(
    price: float,
) -> Candle:

    return Candle(
        timestamp=datetime(
            2025,
            1,
            1,
        ),
        open=price,
        high=price + 1,
        low=price - 1,
        close=price,
        volume=1000,
    )


def test_risk_config_percentage_is_correct():

    config = RiskConfig(
        risk_per_trade=1.0
    )

    assert config.risk_per_trade == 1.0



def test_risk_manager_approves_valid_order():

    portfolio = create_portfolio()

    risk_manager = RiskManager(
        portfolio
    )


    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=100,
        price=100,
    )


    approved, reason = risk_manager.validate(
        order
    )


    assert approved is True
    assert reason == "Approved"



def test_risk_manager_rejects_excessive_order():

    portfolio = create_portfolio()

    risk_manager = RiskManager(
        portfolio
    )


    order = TradeOrder(
        symbol="RR.L",
        action=SignalType.BUY,
        quantity=2000,
        price=100,
    )


    approved, _ = risk_manager.validate(
        order
    )


    assert approved is False