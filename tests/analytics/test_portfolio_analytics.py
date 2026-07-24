"""
===========================================================
TradePilotAI
Portfolio Analytics Tests
===========================================================

Tests the PortfolioAnalytics class.
"""

from datetime import datetime

from analytics.portfolio_analytics import PortfolioAnalytics
from models.trade import Trade
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount


def create_trade(
    entry_price: float,
    exit_price: float,
) -> Trade:
    """
    Create a completed trade for testing.
    """

    return Trade(
        symbol="AAPL",
        quantity=10,
        entry_price=entry_price,
        exit_price=exit_price,
        entry_date=datetime(2026, 1, 1),
        exit_date=datetime(2026, 1, 2),
        strategy="Unit Test",
    )


def test_portfolio_statistics():
    """
    Portfolio statistics should be calculated correctly.
    """

    account = SimulationAccount(10_000)

    portfolio = PortfolioManager(account)

    # Winning trade (+100)
    portfolio.record_trade(create_trade(100, 110))

    # Losing trade (-100)
    portfolio.record_trade(create_trade(100, 90))

    # Winning trade (+200)
    portfolio.record_trade(create_trade(100, 120))

    analytics = PortfolioAnalytics(portfolio)

    assert analytics.total_trades == 3
    assert analytics.winning_trades == 2
    assert analytics.losing_trades == 1
    assert analytics.realised_profit == 300
    assert analytics.realised_loss == -100
    assert analytics.net_profit == 200