"""Deterministic golden research dataset for backtesting UI and regression checks."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from datetime import timedelta
from typing import Any

from .result import BacktestResult
from .result import BacktestTradeRecord


@dataclass(frozen=True, slots=True)
class GoldenResearchDataset:
    """Reusable deterministic fixture payload for research and UI verification."""

    result: BacktestResult
    trade_history: list[dict[str, Any]]
    monthly_returns: list[tuple[str, float]]


MONTHLY_RETURNS: list[tuple[str, float]] = [
    ("2022-01", 1.20),
    ("2022-02", -0.59),
    ("2022-03", 1.49),
    ("2022-04", 1.27),
    ("2022-05", -0.68),
    ("2022-06", 1.75),
    ("2022-07", 1.24),
    ("2022-08", -0.85),
    ("2022-09", 1.33),
    ("2022-10", 0.75),
    ("2022-11", -0.56),
    ("2022-12", 1.78),
    ("2023-01", 1.38),
    ("2023-02", -1.09),
    ("2023-03", 1.66),
    ("2023-04", 1.18),
    ("2023-05", -0.81),
    ("2023-06", 2.07),
    ("2023-07", 1.24),
    ("2023-08", -1.05),
    ("2023-09", 2.03),
    ("2023-10", 1.04),
    ("2023-11", -0.77),
    ("2023-12", 1.55),
    ("2024-01", 1.35),
    ("2024-02", -0.99),
    ("2024-03", 1.75),
    ("2024-04", 2.13),
    ("2024-05", -1.04),
    ("2024-06", 1.94),
    ("2024-07", -2.62),
    ("2024-08", -2.36),
    ("2024-09", -3.26),
    ("2024-10", 2.93),
    ("2024-11", 4.65),
    ("2024-12", 2.45),
]


EQUITY_CURVE: list[tuple[str, float]] = [
    ("2022-01-31", 100000.0),
    ("2022-02-28", 101200.0),
    ("2022-03-31", 100600.0),
    ("2022-04-30", 102100.0),
    ("2022-05-31", 103400.0),
    ("2022-06-30", 102700.0),
    ("2022-07-31", 104500.0),
    ("2022-08-31", 105800.0),
    ("2022-09-30", 104900.0),
    ("2022-10-31", 106300.0),
    ("2022-11-30", 107100.0),
    ("2022-12-31", 106500.0),
    ("2023-01-31", 108400.0),
    ("2023-02-28", 109900.0),
    ("2023-03-31", 108700.0),
    ("2023-04-30", 110500.0),
    ("2023-05-31", 111800.0),
    ("2023-06-30", 110900.0),
    ("2023-07-31", 113200.0),
    ("2023-08-31", 114600.0),
    ("2023-09-30", 113400.0),
    ("2023-10-31", 115700.0),
    ("2023-11-30", 116900.0),
    ("2023-12-31", 116000.0),
    ("2024-01-31", 119800.0),
    ("2024-02-29", 121400.0),
    ("2024-03-31", 120200.0),
    ("2024-04-30", 122300.0),
    ("2024-05-31", 124900.0),
    ("2024-06-30", 123600.0),
    ("2024-07-31", 126000.0),
    ("2024-08-31", 122700.0),
    ("2024-09-30", 119800.0),
    ("2024-10-31", 115900.0),
    ("2024-11-30", 119300.0),
    ("2024-12-31", 124850.0),
]


DRAWDOWN_SERIES: list[tuple[str, float]] = [
    ("2022-01-31", 0.00),
    ("2022-02-28", 0.00),
    ("2022-03-31", -0.59),
    ("2022-04-30", 0.00),
    ("2022-05-31", 0.00),
    ("2022-06-30", -0.68),
    ("2022-07-31", 0.00),
    ("2022-08-31", 0.00),
    ("2022-09-30", -0.85),
    ("2022-10-31", 0.00),
    ("2022-11-30", 0.00),
    ("2022-12-31", -0.56),
    ("2023-01-31", 0.00),
    ("2023-02-28", 0.00),
    ("2023-03-31", -1.09),
    ("2023-04-30", 0.00),
    ("2023-05-31", 0.00),
    ("2023-06-30", -0.81),
    ("2023-07-31", 0.00),
    ("2023-08-31", 0.00),
    ("2023-09-30", -1.05),
    ("2023-10-31", 0.00),
    ("2023-11-30", 0.00),
    ("2023-12-31", -0.77),
    ("2024-01-31", 0.00),
    ("2024-02-29", 0.00),
    ("2024-03-31", -0.99),
    ("2024-04-30", 0.00),
    ("2024-05-31", 0.00),
    ("2024-06-30", -1.04),
    ("2024-07-31", 0.00),
    ("2024-08-31", -2.62),
    ("2024-09-30", -4.92),
    ("2024-10-31", -8.02),
    ("2024-11-30", -5.32),
    ("2024-12-31", -0.91),
]


def create_golden_research_dataset() -> GoldenResearchDataset:
    """Build a deterministic fixture with a realistic multi-year result."""

    closed_trades = _build_closed_trades()
    trade_history = [_trade_record_to_history_row(trade) for trade in closed_trades]
    exit_breakdown = Counter(trade.exit_reason for trade in closed_trades)

    result = BacktestResult(initial_cash=100000.0)
    result.requested_symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL"]
    result.loaded_symbols = list(result.requested_symbols)
    result.failed_symbols = {}
    result.completion_status = "success"

    result.closed_trades = closed_trades
    result.trades = list(closed_trades)
    result.equity_curve = list(EQUITY_CURVE)
    result.running_equity = list(EQUITY_CURVE)
    result.drawdown_series = list(DRAWDOWN_SERIES)
    result.drawdown_curve = list(DRAWDOWN_SERIES)
    result.peak_equity = _build_peak_equity(EQUITY_CURVE)

    result.portfolio.cash = 124850.0
    result.portfolio.realised_pnl = 24850.0
    result.portfolio.unrealised_pnl = 0.0
    result.portfolio.exposure = 0.0
    result.portfolio.metadata.update(
        {
            "dataset": "golden_research",
            "base_currency": "GBP",
            "initial_capital": 100000.0,
            "final_equity": 124850.0,
            "date_range": "2022-01-01 to 2024-12-31",
        }
    )

    result.symbol_results = {
        "AAPL": {"status": "completed", "signals": 68, "closed_trades": 36},
        "MSFT": {"status": "completed", "signals": 62, "closed_trades": 34},
        "NVDA": {"status": "completed", "signals": 58, "closed_trades": 34},
        "TSLA": {"status": "completed", "signals": 71, "closed_trades": 36},
        "AMZN": {"status": "completed", "signals": 63, "closed_trades": 35},
        "META": {"status": "completed", "signals": 57, "closed_trades": 35},
        "GOOGL": {"status": "completed", "signals": 56, "closed_trades": 35},
    }

    result.metrics = {
        "net_profit": 24850.0,
        "total_return": 0.2485,
        "profit_factor": 2.1,
        "win_rate": 61.2,
        "maximum_drawdown": -8.02,
        "expectancy": 101.43,
        "final_equity": 124850.0,
        "total_trades": len(closed_trades),
        "exit_reason_breakdown": dict(exit_breakdown),
        "monthly_returns": list(MONTHLY_RETURNS),
    }

    return GoldenResearchDataset(
        result=result,
        trade_history=trade_history,
        monthly_returns=list(MONTHLY_RETURNS),
    )


def create_golden_backtest_result() -> BacktestResult:
    """Return only the deterministic BacktestResult for consumers that need it."""

    return create_golden_research_dataset().result


def _build_closed_trades() -> list[BacktestTradeRecord]:
    symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL"]
    trades: list[BacktestTradeRecord] = []
    start = date(2022, 1, 3)

    for index in range(245):
        symbol = symbols[index % len(symbols)]
        direction = "BUY" if index % 2 == 0 else "SELL"
        is_win = (index % 8) not in {1, 6, 7}

        entry_date = start + timedelta(days=index * 4)
        exit_date = entry_date + timedelta(days=2 + (index % 9))

        entry_price = 78.0 + (index % 40) * 2.15
        move = 1.05 + (index % 5) * 0.35

        if direction == "BUY":
            exit_price = entry_price + move if is_win else entry_price - move
        else:
            exit_price = entry_price - move if is_win else entry_price + move

        quantity = 10 + (index % 15)
        costs = 6.0 + (index % 5) * 1.25
        gross_pnl = (220.0 + (index % 7) * 18.0) if is_win else -(140.0 + (index % 5) * 22.0)
        net_pnl = gross_pnl - costs if is_win else gross_pnl - costs

        if index == 244:
            exit_reason = "End of Test"
        elif is_win and (index % 4 in {0, 2}):
            exit_reason = "Take Profit"
        elif is_win:
            exit_reason = "Strategy Exit"
        elif index % 6 == 0:
            exit_reason = "Strategy Exit"
        else:
            exit_reason = "Stop Loss"

        stop_loss = entry_price - 1.8 if direction == "BUY" else entry_price + 1.8
        take_profit = entry_price + 2.6 if direction == "BUY" else entry_price - 2.6

        trades.append(
            BacktestTradeRecord(
                symbol=symbol,
                direction=direction,
                entry_date=entry_date.isoformat(),
                entry_price=round(entry_price, 2),
                exit_date=exit_date.isoformat(),
                exit_price=round(exit_price, 2),
                quantity=quantity,
                gross_pnl=round(gross_pnl, 2),
                costs=round(costs, 2),
                net_pnl=round(net_pnl, 2),
                exit_reason=exit_reason,
                stop_loss=round(stop_loss, 2),
                take_profit=round(take_profit, 2),
                commission=round(costs * 0.52, 2),
                spread_cost=round(costs * 0.30, 2),
                slippage_cost=round(costs * 0.18, 2),
                reference_entry_price=round(entry_price, 2),
                reference_exit_price=round(exit_price, 2),
            )
        )

    return trades


def _build_peak_equity(equity_curve: list[tuple[str, float]]) -> list[tuple[str, float]]:
    peaks: list[tuple[str, float]] = []
    high = 0.0
    for timestamp, value in equity_curve:
        if value > high:
            high = value
        peaks.append((timestamp, high))
    return peaks


def _trade_record_to_history_row(record: BacktestTradeRecord) -> dict[str, Any]:
    return {
        "symbol": record.symbol,
        "direction": record.direction,
        "entry_date": record.entry_date,
        "entry_price": record.entry_price,
        "exit_date": record.exit_date,
        "exit_price": record.exit_price,
        "quantity": record.quantity,
        "net_pnl": record.net_pnl,
        "exit_reason": record.exit_reason,
    }
