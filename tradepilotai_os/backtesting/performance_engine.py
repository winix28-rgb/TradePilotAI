"""Performance analysis for TradePilotAI backtests."""

from __future__ import annotations

from collections.abc import Iterable
from collections import Counter
from datetime import datetime
from math import sqrt
from statistics import mean
from statistics import pstdev
from typing import Any

from tradepilotai_os.backtesting.result import BacktestResult


class PerformanceEngine:
    """Compute standard backtest performance metrics."""

    def evaluate(self, result: BacktestResult) -> dict[str, Any]:
        closed_trades = [trade for trade in result.closed_trades if trade.net_pnl is not None]
        if not closed_trades:
            result.running_equity = list(result.equity_curve)
            result.peak_equity = self._peak_equity_curve(result.equity_curve)
            result.drawdown_series = self.build_drawdown_curve(result.equity_curve)
            result.drawdown_curve = list(result.drawdown_series)
            return {
                "net_profit": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "total_return": 0.0,
                "cagr": 0.0,
                "total_trades": 0,
                "number_of_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "profit_factor": 0.0,
                "expectancy": 0.0,
                "maximum_drawdown": 0.0,
                "average_drawdown": 0.0,
                "recovery_factor": 0.0,
                "largest_winner": 0.0,
                "largest_loser": 0.0,
                "maximum_consecutive_winners": 0,
                "maximum_consecutive_losers": 0,
                "average_winner": 0.0,
                "average_loser": 0.0,
                "average_holding_period": 0.0,
                "average_trade_duration": 0.0,
                "long_trades": 0,
                "short_trades": 0,
                "long_win_rate": 0.0,
                "short_win_rate": 0.0,
                "exit_reason_breakdown": {},
                "equity_curve": list(result.equity_curve),
                "running_equity": list(result.running_equity),
                "peak_equity": list(result.peak_equity),
                "drawdown_series": list(result.drawdown_series),
            }

        ordered_trades = self._ordered_trades(closed_trades)
        profits = [float(trade.net_pnl or 0.0) for trade in ordered_trades]
        gross_profits = [float(trade.gross_pnl or 0.0) for trade in ordered_trades]
        costs = [float(trade.costs or 0.0) for trade in ordered_trades]
        wins = [profit for profit in profits if profit > 0]
        losses = [profit for profit in profits if profit < 0]

        start_equity = float(result.initial_cash or result.portfolio.metadata.get("initial_cash", 0.0) or 0.0)
        ending_equity = float(result.portfolio.cash + result.portfolio.unrealised_pnl)
        net_profit = sum(profits)
        gross_profit = sum(profit for profit in gross_profits if profit > 0)
        gross_loss = abs(sum(profit for profit in gross_profits if profit < 0))
        total_return = (net_profit / start_equity * 100.0) if start_equity else 0.0

        win_rate = (len(wins) / len(ordered_trades) * 100.0) if ordered_trades else 0.0
        loss_rate = (len(losses) / len(ordered_trades) * 100.0) if ordered_trades else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss else (float("inf") if gross_profit > 0 else 0.0)
        expectancy = (net_profit / len(ordered_trades)) if ordered_trades else 0.0

        running_equity = self._running_equity_curve(result.equity_curve)
        peak_equity = self._peak_equity_curve(result.equity_curve)
        drawdown_series = self.build_drawdown_curve(result.equity_curve)
        result.running_equity = running_equity
        result.peak_equity = peak_equity
        result.drawdown_series = drawdown_series
        result.drawdown_curve = list(drawdown_series)

        max_drawdown = self._max_drawdown(result.equity_curve)
        average_drawdown = self._average_drawdown(drawdown_series)
        recovery_factor = self._recovery_factor(net_profit, result.equity_curve)
        cagr = self._cagr(result.equity_curve, start_equity, ending_equity)
        largest_winner = max(wins) if wins else 0.0
        largest_loser = min(losses) if losses else 0.0
        maximum_consecutive_winners, maximum_consecutive_losers = self._consecutive_runs(ordered_trades)
        average_winner = mean(wins) if wins else 0.0
        average_loser = mean(losses) if losses else 0.0
        average_holding_period = self._average_holding_period_days(ordered_trades)
        average_trade_duration = self._average_trade_duration_hours(ordered_trades)
        long_trades, short_trades, long_win_rate, short_win_rate = self._directional_metrics(ordered_trades)
        exit_reason_breakdown = self._exit_reason_breakdown(ordered_trades)

        metrics = {
            "net_profit": round(net_profit, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "total_return": round(total_return, 2),
            "cagr": round(cagr, 2),
            "total_trades": len(ordered_trades),
            "number_of_trades": len(ordered_trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else profit_factor,
            "expectancy": round(expectancy, 2),
            "maximum_drawdown": round(max_drawdown, 2),
            "average_drawdown": round(average_drawdown, 2),
            "recovery_factor": round(recovery_factor, 2),
            "largest_winner": round(largest_winner, 2),
            "largest_loser": round(largest_loser, 2),
            "maximum_consecutive_winners": maximum_consecutive_winners,
            "maximum_consecutive_losers": maximum_consecutive_losers,
            "average_winner": round(average_winner, 2),
            "average_loser": round(average_loser, 2),
            "average_holding_period": round(average_holding_period, 2),
            "average_trade_duration": round(average_trade_duration, 2),
            "long_trades": long_trades,
            "short_trades": short_trades,
            "long_win_rate": round(long_win_rate, 2),
            "short_win_rate": round(short_win_rate, 2),
            "exit_reason_breakdown": exit_reason_breakdown,
            "equity_curve": list(result.equity_curve),
            "running_equity": list(result.running_equity),
            "peak_equity": list(result.peak_equity),
            "drawdown_series": list(result.drawdown_series),
            "costs": round(sum(costs), 2),
            "sharpe_ratio": round(self._sharpe_ratio(self._equity_returns(result.equity_curve)), 2),
        }

        result.metrics = metrics
        return metrics

    def build_drawdown_curve(self, equity_curve: Iterable[tuple[Any, float]]) -> list[tuple[Any, float]]:
        """Return a drawdown series from an equity curve."""

        peak = 0.0
        drawdowns: list[tuple[Any, float]] = []
        for timestamp, equity in equity_curve:
            peak = max(peak, float(equity))
            drawdown = 0.0 if peak == 0 else ((float(equity) - peak) / peak) * 100.0
            drawdowns.append((timestamp, round(drawdown, 2)))
        return drawdowns

    def _running_equity_curve(self, equity_curve: Iterable[tuple[Any, float]]) -> list[tuple[Any, float]]:
        return [(timestamp, round(float(equity), 2)) for timestamp, equity in equity_curve]

    def _peak_equity_curve(self, equity_curve: Iterable[tuple[Any, float]]) -> list[tuple[Any, float]]:
        peak = 0.0
        peaks: list[tuple[Any, float]] = []
        for timestamp, equity in equity_curve:
            peak = max(peak, float(equity))
            peaks.append((timestamp, round(peak, 2)))
        return peaks

    def _equity_returns(self, equity_curve: Iterable[tuple[Any, float]]) -> list[float]:
        values = [float(equity) for _, equity in equity_curve]
        if len(values) < 2:
            return []
        returns: list[float] = []
        for previous, current in zip(values, values[1:]):
            if previous == 0:
                continue
            returns.append((current - previous) / previous)
        return returns

    def _sharpe_ratio(self, returns: list[float]) -> float:
        if len(returns) < 2:
            return 0.0
        volatility = pstdev(returns)
        if volatility == 0:
            return 0.0
        return (mean(returns) / volatility) * sqrt(len(returns))

    def _max_drawdown(self, equity_curve: Iterable[tuple[Any, float]]) -> float:
        peak = 0.0
        worst = 0.0
        for _, equity in equity_curve:
            peak = max(peak, float(equity))
            if peak == 0:
                continue
            drawdown = ((float(equity) - peak) / peak) * 100.0
            worst = min(worst, drawdown)
        return worst

    def _average_drawdown(self, equity_curve: Iterable[tuple[Any, float]]) -> float:
        values = [float(value) for _, value in equity_curve if float(value) < 0]
        return mean(values) if values else 0.0

    def _recovery_factor(self, net_profit: float, equity_curve: Iterable[tuple[Any, float]]) -> float:
        peak = 0.0
        worst_drawdown_amount = 0.0
        for _, equity in equity_curve:
            current = float(equity)
            peak = max(peak, current)
            worst_drawdown_amount = max(worst_drawdown_amount, peak - current)
        if worst_drawdown_amount <= 0:
            return float("inf") if net_profit > 0 else 0.0
        return net_profit / worst_drawdown_amount

    def _ordered_trades(self, trades: list[Any]) -> list[Any]:
        def _sort_key(trade: Any) -> tuple[Any, Any]:
            return (
                getattr(trade, "exit_date", None) or getattr(trade, "exit_time", None) or 0,
                getattr(trade, "entry_date", None) or getattr(trade, "entry_time", None) or 0,
            )

        return sorted(trades, key=_sort_key)

    def _consecutive_runs(self, trades: list[Any]) -> tuple[int, int]:
        max_winners = 0
        max_losers = 0
        current_winners = 0
        current_losers = 0
        for trade in trades:
            pnl = float(getattr(trade, "net_pnl", 0.0) or 0.0)
            if pnl > 0:
                current_winners += 1
                current_losers = 0
            elif pnl < 0:
                current_losers += 1
                current_winners = 0
            else:
                current_winners = 0
                current_losers = 0
            max_winners = max(max_winners, current_winners)
            max_losers = max(max_losers, current_losers)
        return max_winners, max_losers

    def _average_holding_period_days(self, trades: list[Any]) -> float:
        durations = [self._duration_days(trade) for trade in trades if self._duration_days(trade) is not None]
        return mean(durations) if durations else 0.0

    def _average_trade_duration_hours(self, trades: list[Any]) -> float:
        durations = [self._duration_hours(trade) for trade in trades if self._duration_hours(trade) is not None]
        return mean(durations) if durations else 0.0

    def _duration_days(self, trade: Any) -> float | None:
        duration = self._trade_duration_seconds(trade)
        if duration is None:
            return None
        return duration / 86400.0

    def _duration_hours(self, trade: Any) -> float | None:
        duration = self._trade_duration_seconds(trade)
        if duration is None:
            return None
        return duration / 3600.0

    def _trade_duration_seconds(self, trade: Any) -> float | None:
        start = getattr(trade, "entry_date", None) or getattr(trade, "entry_time", None)
        end = getattr(trade, "exit_date", None) or getattr(trade, "exit_time", None)
        if start is None or end is None:
            return None
        if isinstance(start, datetime) and isinstance(end, datetime):
            return max(0.0, (end - start).total_seconds())
        try:
            return max(0.0, float(end - start))
        except Exception:
            return None

    def _directional_metrics(self, trades: list[Any]) -> tuple[int, int, float, float]:
        long_trades = [trade for trade in trades if str(getattr(trade, "direction", "")).lower() == "long"]
        short_trades = [trade for trade in trades if str(getattr(trade, "direction", "")).lower() == "short"]
        long_wins = [trade for trade in long_trades if float(getattr(trade, "net_pnl", 0.0) or 0.0) > 0]
        short_wins = [trade for trade in short_trades if float(getattr(trade, "net_pnl", 0.0) or 0.0) > 0]
        long_win_rate = (len(long_wins) / len(long_trades) * 100.0) if long_trades else 0.0
        short_win_rate = (len(short_wins) / len(short_trades) * 100.0) if short_trades else 0.0
        return len(long_trades), len(short_trades), long_win_rate, short_win_rate

    def _exit_reason_breakdown(self, trades: list[Any]) -> dict[str, int]:
        counts = Counter(self._normalize_exit_reason(getattr(trade, "exit_reason", None)) for trade in trades)
        ordered_labels = ["Stop Loss", "Take Profit", "Strategy Exit", "End of Test"]
        return {label: counts.get(label, 0) for label in ordered_labels}

    def _normalize_exit_reason(self, exit_reason: Any) -> str:
        reason = str(exit_reason or "").strip().lower().replace("_", " ")
        if reason in {"stop", "stop loss", "stoploss"}:
            return "Stop Loss"
        if reason in {"target", "take profit", "takeprofit"}:
            return "Take Profit"
        if reason in {"strategy exit", "strategy"}:
            return "Strategy Exit"
        if reason in {"end of test", "eod", "end of backtest"}:
            return "End of Test"
        return "Strategy Exit"

    def _cagr(self, equity_curve: Iterable[tuple[Any, float]], start_equity: float, ending_equity: float) -> float:
        points = list(equity_curve)
        if not points or start_equity <= 0 or ending_equity <= 0:
            return 0.0

        first_timestamp = points[0][0]
        last_timestamp = points[-1][0]
        days = self._days_between(first_timestamp, last_timestamp)
        if days <= 0:
            return 0.0

        years = days / 365.0
        if years <= 0:
            return 0.0
        return ((ending_equity / start_equity) ** (1 / years) - 1) * 100.0

    def _days_between(self, start: Any, end: Any) -> float:
        if isinstance(start, datetime) and isinstance(end, datetime):
            return max(0.0, (end - start).total_seconds() / 86400.0)
        try:
            return max(0.0, float(end - start))
        except Exception:
            return 0.0