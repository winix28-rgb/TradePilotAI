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


def create_report():
    """
    Create a populated performance report for testing.
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
        equity_curve=[
            EquityPoint(
                timestamp=datetime(2025, 1, 1),
                equity=10_000,
            )
        ],
    )

    return PerformanceReport(result)


def test_performance_report_exposes_backtest_objects():

    report = create_report()

    assert report.result is not None
    assert report.analytics is not None
    assert report.portfolio is not None
    assert report.equity_curve is not None


def test_performance_metrics():

    report = create_report()

    assert report.win_rate == 50.0
    assert report.profit_factor == 2.0
    assert report.average_winner == 1000.0
    assert report.average_loser == -500.0
    assert report.largest_winner == 1000.0
    assert report.largest_loser == -500.0
    assert report.expectancy == 250.0


def test_to_text_contains_expected_sections():

    report = create_report()

    text = report.to_text()

    assert "TradePilotAI Strategy Report" in text
    assert "BACKTEST" in text
    assert "TRADING" in text
    assert "Win Rate" in text
    assert "Profit Factor" in text
    assert "Expectancy" in text
    assert "Largest Winner" in text


def test_str_returns_text_report():

    report = create_report()

    assert str(report) == report.to_text()


def test_empty_performance_metrics():

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
    assert report.expectancy == 0.0