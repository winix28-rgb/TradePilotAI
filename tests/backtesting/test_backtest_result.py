"""
===========================================================
TradePilotAI
Backtest Result Tests
===========================================================
"""

from datetime import datetime

from analytics.portfolio_analytics import PortfolioAnalytics
from backtesting.backtest_result import BacktestResult
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount


def test_backtest_result_returns():

    account = SimulationAccount(10_000)

    portfolio = PortfolioManager(account)

    analytics = PortfolioAnalytics(portfolio)

    result = BacktestResult(
        portfolio=portfolio,
        analytics=analytics,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 12, 31),
        initial_cash=10_000,
        final_value=11_500,
    )

    assert result.net_profit == 1500

    assert result.return_percent == 15