"""
===========================================================
TradePilotAI
Performance Report Tests
===========================================================
"""

from datetime import datetime

from analytics.performance_report import PerformanceReport
from analytics.portfolio_analytics import PortfolioAnalytics
from backtesting.backtest_result import BacktestResult
from backtesting.equity_point import EquityPoint
from models.trade import Trade
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount


def test_performance_report_exposes_backtest_objects():
    """
    PerformanceReport should expose the underlying backtest objects.
    """

    account = SimulationAccount(10_000)

    portfolio = PortfolioManager(account)

    analytics = PortfolioAnalytics(portfolio)

    equity_curve = [
        EquityPoint(
            timestamp=datetime(2025, 1, 1),
            equity=10_000,
        )
    ]

    result = BacktestResult(
        portfolio=portfolio,
        analytics=analytics,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 12, 31),
        initial_cash=10_000,
        final_value=10_000,
        equity_curve=equity_curve,
    )

    report = PerformanceReport(result)

    assert report.result is result
    assert report.analytics is analytics
    assert report.portfolio is portfolio
    assert report.equity_curve is equity_curve


def test_performance_metrics():
    """
    Performance metrics should be calculated correctly.
    """

    account = SimulationAccount(10_000)

    portfolio = PortfolioManager(account)

    portfolio.record_trade(
        Trade(
            symbol="ABC",
            quantity=100,
            entry_price=100,
            exit_price=110,
            entry_date=datetime(2025, 1, 1),
            exit_date=datetime(2025, 1, 2),
        )
    )

    portfolio.record_trade(
        Trade(
            symbol="XYZ",
            quantity=100,
            entry_price=100,
            exit_price=95,
            entry_date=datetime(2025, 1, 3),
            exit_date=datetime(2025, 1, 4),
        )
    )

    analytics = PortfolioAnalytics(portfolio)

    result = BacktestResult(
        portfolio=portfolio,
        analytics=analytics,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 31),
        initial_cash=10_000,
        final_value=10_500,
        equity_curve=[],
    )

    report = PerformanceReport(result)

    assert report.win_rate == 50.0
    assert report.profit_factor == 2.0

    assert report.average_winner == 1000.0
    assert report.average_loser == -500.0

    assert report.largest_winner == 1000.0
    assert report.largest_loser == -500.0


def test_empty_performance_metrics():
    """
    Empty portfolios should return zero-valued metrics.
    """

    account = SimulationAccount(10_000)

    portfolio = PortfolioManager(account)

    analytics = PortfolioAnalytics(portfolio)

    result = BacktestResult(
        portfolio=portfolio,
        analytics=analytics,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 31),
        initial_cash=10_000,
        final_value=10_000,
        equity_curve=[],
    )

    report = PerformanceReport(result)

    assert report.win_rate == 0.0
    assert report.profit_factor == 0.0

    assert report.average_winner == 0.0
    assert report.average_loser == 0.0

    assert report.largest_winner == 0.0
    assert report.largest_loser == 0.0