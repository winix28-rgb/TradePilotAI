from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from tradepilotai_os.backtesting import BacktestResult, BacktestTradeRecord, PerformanceEngine


def make_trade(
    symbol: str,
    direction: str,
    net_pnl: float,
    exit_reason: str,
    entry_offset_days: int,
    holding_hours: int = 24,
) -> BacktestTradeRecord:
    entry_date = datetime(2025, 1, 1) + timedelta(days=entry_offset_days)
    exit_date = entry_date + timedelta(hours=holding_hours)
    return BacktestTradeRecord(
        symbol=symbol,
        direction=direction,
        entry_date=entry_date,
        entry_price=100.0,
        exit_date=exit_date,
        exit_price=101.0,
        quantity=1,
        gross_pnl=net_pnl,
        costs=0.0,
        net_pnl=net_pnl,
        exit_reason=exit_reason,
        stop_loss=95.0,
        take_profit=110.0,
        commission=0.0,
        spread_cost=0.0,
        slippage_cost=0.0,
        reference_entry_price=100.0,
        reference_exit_price=101.0,
    )


def make_result(trades: list[BacktestTradeRecord]) -> BacktestResult:
    result = BacktestResult(initial_cash=1000.0)
    result.closed_trades = list(trades)
    result.trades = list(trades)
    result.portfolio.cash = 1020.0
    result.portfolio.metadata["initial_cash"] = 1000.0
    result.equity_curve = [
        (datetime(2025, 1, 1), 1000.0),
        (datetime(2025, 1, 2), 1200.0),
        (datetime(2025, 1, 3), 900.0),
        (datetime(2025, 1, 4), 1000.0),
        (datetime(2025, 1, 5), 1020.0),
    ]
    return result


def test_performance_engine_profit_factor_and_expectancy():
    result = make_result(
        [
            make_trade("AAPL", "Long", 10.0, "Take Profit", 0),
            make_trade("MSFT", "Long", -5.0, "Stop Loss", 1),
            make_trade("TSLA", "Short", 15.0, "Strategy Exit", 2),
        ]
    )

    metrics = PerformanceEngine().evaluate(result)

    assert metrics["profit_factor"] == pytest.approx(5.0)
    assert metrics["expectancy"] == pytest.approx(6.67, rel=1e-2)
    assert metrics["gross_profit"] == pytest.approx(25.0)
    assert metrics["gross_loss"] == pytest.approx(5.0)


def test_performance_engine_drawdown_and_consecutive_runs():
    result = make_result(
        [
            make_trade("AAPL", "Long", 8.0, "Take Profit", 0),
            make_trade("MSFT", "Long", 7.0, "Take Profit", 1),
            make_trade("TSLA", "Short", -4.0, "Stop Loss", 2),
            make_trade("NVDA", "Short", -3.0, "Stop Loss", 3),
            make_trade("AMD", "Long", -2.0, "Strategy Exit", 4),
            make_trade("ORCL", "Long", 11.0, "End of Test", 5),
        ]
    )

    metrics = PerformanceEngine().evaluate(result)

    assert metrics["maximum_drawdown"] == pytest.approx(-25.0)
    assert metrics["maximum_consecutive_winners"] == 2
    assert metrics["maximum_consecutive_losers"] == 3


def test_performance_engine_exit_reason_breakdown():
    result = make_result(
        [
            make_trade("AAPL", "Long", 8.0, "Take Profit", 0),
            make_trade("MSFT", "Long", -4.0, "Stop Loss", 1),
            make_trade("TSLA", "Short", 5.0, "Strategy Exit", 2),
            make_trade("NVDA", "Short", 1.0, "End of Test", 3),
        ]
    )

    metrics = PerformanceEngine().evaluate(result)

    assert metrics["exit_reason_breakdown"] == {
        "Stop Loss": 1,
        "Take Profit": 1,
        "Strategy Exit": 1,
        "End of Test": 1,
    }


def test_performance_engine_portfolio_series_are_populated():
    result = make_result([make_trade("AAPL", "Long", 10.0, "Take Profit", 0)])

    metrics = PerformanceEngine().evaluate(result)

    assert result.running_equity
    assert result.peak_equity
    assert result.drawdown_series
    assert metrics["equity_curve"] == result.equity_curve
    assert metrics["running_equity"] == result.running_equity
    assert metrics["peak_equity"] == result.peak_equity
    assert metrics["drawdown_series"] == result.drawdown_series