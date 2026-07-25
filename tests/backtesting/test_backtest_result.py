"""
===========================================================
TradePilotAI
Backtest Result Tests
===========================================================
"""

from datetime import datetime

from analytics.portfolio_analytics import PortfolioAnalytics
from backtesting.backtest_result import BacktestResult
from backtesting.equity_point import EquityPoint
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount


def test_backtest_result_returns():

    account = SimulationAccount(10_000)

    portfolio = PortfolioManager(account)

    analytics = PortfolioAnalytics(portfolio)

    equity_curve = [
        EquityPoint(
            timestamp=datetime(2025, 1, 1),
            equity=10_000,
        ),
        EquityPoint(
            timestamp=datetime(2025, 12, 31),
            equity=11_500,
        ),
    ]

    result = BacktestResult(
        portfolio=portfolio,
        analytics=analytics,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 12, 31),
        initial_cash=10_000,
        final_value=11_500,
        equity_curve=equity_curve,
    )

    assert result.net_profit == 1500

    assert result.return_percent == 15

    assert len(result.equity_curve) == 2

    assert result.equity_curve[0].equity == 10_000

    assert result.equity_curve[-1].equity == 11_500