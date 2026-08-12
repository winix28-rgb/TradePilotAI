"""Centralized analytics engine for the performance dashboard."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from statistics import mean
from typing import Any

from .models import PerformanceDashboard
from .models import TradeRecord


class PerformanceEngine:
    """Own all performance calculations across paper and backtesting data sources."""

    def build_dashboard(
        self,
        *,
        paper_portfolio: dict[str, Any],
        paper_closed_trades: list[dict[str, Any]],
        trade_journal_entries: list[dict[str, Any]],
        backtest_payload: dict[str, Any],
        strategy_comparison_payload: dict[str, Any],
    ) -> PerformanceDashboard:
        start_equity = self._resolve_starting_equity(paper_portfolio)
        trades = self._normalize_trades(
            paper_closed_trades=paper_closed_trades,
            trade_journal_entries=trade_journal_entries,
            backtest_payload=backtest_payload,
        )

        equity_points = self._equity_curve_points(trades, start_equity)
        drawdown_series = self._drawdown_series(equity_points)
        portfolio_overview = self._portfolio_overview(paper_portfolio, trades)
        performance_kpis = self._performance_kpis(trades, drawdown_series, start_equity)
        trade_analysis = self._trade_analysis(trades)
        exit_analysis = self._exit_analysis(trades)
        strategy_analysis = self._strategy_analysis(trades, start_equity)
        time_analysis = self._time_analysis(trades)
        long_short_analysis = self._long_short_analysis(trades)
        asset_analysis = self._asset_analysis(trades)
        risk_analysis = self._risk_analysis(trades, paper_portfolio)

        charts = {
            "equity_curve": [{"timestamp": ts, "equity": eq} for ts, eq in equity_points],
            "drawdown_curve": [{"timestamp": ts, "drawdown": dd} for ts, dd in drawdown_series],
            "monthly_returns": self._monthly_return_rows(equity_points),
            "strategy_comparison": list((strategy_comparison_payload or {}).get("table", []) or strategy_analysis),
            "exit_distribution": exit_analysis,
            "win_loss_distribution": [
                {"label": "Wins", "count": trade_analysis["winning_trades"]},
                {"label": "Losses", "count": trade_analysis["losing_trades"]},
            ],
            "portfolio_growth": [{"timestamp": ts, "value": eq - start_equity} for ts, eq in equity_points],
        }

        return PerformanceDashboard(
            generated_at=datetime.now(timezone.utc).isoformat(),
            portfolio_overview=portfolio_overview,
            performance_kpis=performance_kpis,
            equity_curve={
                "running_equity": [{"timestamp": ts, "value": eq} for ts, eq in equity_points],
                "peak_equity": self._peak_rows(equity_points),
                "drawdown_overlay": [{"timestamp": ts, "value": dd} for ts, dd in drawdown_series],
            },
            drawdown=self._drawdown_summary(drawdown_series),
            trade_analysis=trade_analysis,
            strategy_analysis=strategy_analysis,
            exit_analysis=exit_analysis,
            time_analysis=time_analysis,
            long_short_analysis=long_short_analysis,
            asset_analysis=asset_analysis,
            risk_analysis=risk_analysis,
            charts=charts,
            trades=[asdict(item) for item in trades],
            sources={
                "paper_closed_trades": len(paper_closed_trades or []),
                "trade_journal_entries": len(trade_journal_entries or []),
                "backtesting_closed_trades": len((backtest_payload or {}).get("closed_trades", []) or []),
                "strategy_comparison_rows": len((strategy_comparison_payload or {}).get("table", []) or []),
            },
        )

    def _resolve_starting_equity(self, paper_portfolio: dict[str, Any]) -> float:
        current_equity = float((paper_portfolio or {}).get("current_equity", (paper_portfolio or {}).get("portfolio_value", 0.0)) or 0.0)
        total_pnl = float((paper_portfolio or {}).get("total_pnl", 0.0) or 0.0)
        if current_equity > 0:
            return round(current_equity - total_pnl, 2)
        return 100000.0

    def _normalize_trades(
        self,
        *,
        paper_closed_trades: list[dict[str, Any]],
        trade_journal_entries: list[dict[str, Any]],
        backtest_payload: dict[str, Any],
    ) -> list[TradeRecord]:
        normalized: list[TradeRecord] = []
        seen_ids: set[str] = set()

        for row in trade_journal_entries or []:
            trade_id = str(row.get("trade_id", ""))
            if trade_id:
                seen_ids.add(trade_id)
            direction = self._normalize_direction(row.get("direction"))
            risk_snapshot = row.get("risk_snapshot", {}) or {}
            normalized.append(
                TradeRecord(
                    source="paper_journal",
                    trade_id=trade_id,
                    strategy_id=str(row.get("strategy_id", "")),
                    strategy_name=str(row.get("strategy_name", row.get("strategy_id", ""))),
                    symbol=str(row.get("symbol", "")),
                    asset_class=str(row.get("asset_class", "EQUITY") or "EQUITY"),
                    direction=direction,
                    entry_date=str(row.get("entry_date", "")),
                    exit_date=str(row.get("exit_date", "")),
                    entry_price=float(row.get("entry_price", 0.0) or 0.0),
                    exit_price=float(row.get("exit_price", 0.0) or 0.0),
                    quantity=float(row.get("quantity", 0.0) or 0.0),
                    gross_profit=max(0.0, float(row.get("gross_profit", 0.0) or 0.0)),
                    gross_loss=abs(min(0.0, float(row.get("gross_profit", 0.0) or 0.0))),
                    costs=float(row.get("costs", 0.0) or 0.0),
                    net_profit=float(row.get("net_profit", 0.0) or 0.0),
                    exit_reason=self._normalize_exit_reason(row.get("exit_reason")),
                    holding_hours=self._holding_hours(str(row.get("entry_date", "")), str(row.get("exit_date", ""))),
                    risk_percent=float(risk_snapshot.get("risk_percent", 0.0) or 0.0),
                    capital_at_risk=float(risk_snapshot.get("capital_at_risk", 0.0) or 0.0),
                    position_size=float(risk_snapshot.get("position_size", row.get("quantity", 0.0)) or 0.0),
                )
            )

        for row in paper_closed_trades or []:
            trade_id = str(row.get("trade_id", ""))
            if trade_id and trade_id in seen_ids:
                continue
            net_profit = float(row.get("net_profit", 0.0) or 0.0)
            normalized.append(
                TradeRecord(
                    source="paper_closed",
                    trade_id=trade_id,
                    strategy_id=str(row.get("strategy_id", "")),
                    strategy_name=str(row.get("strategy_name", row.get("strategy", row.get("strategy_id", "")))),
                    symbol=str(row.get("symbol", "")),
                    asset_class="EQUITY",
                    direction=self._normalize_direction(row.get("direction")),
                    entry_date=str(row.get("entry_date", "")),
                    exit_date=str(row.get("exit_date", "")),
                    entry_price=float(row.get("entry_price", 0.0) or 0.0),
                    exit_price=float(row.get("exit_price", 0.0) or 0.0),
                    quantity=float(row.get("quantity", 0.0) or 0.0),
                    gross_profit=max(0.0, float(row.get("gross_profit", 0.0) or 0.0)),
                    gross_loss=abs(min(0.0, float(row.get("gross_profit", 0.0) or 0.0))),
                    costs=float(row.get("costs", 0.0) or 0.0),
                    net_profit=net_profit,
                    exit_reason=self._normalize_exit_reason(row.get("exit_reason")),
                    holding_hours=self._holding_hours(str(row.get("entry_date", "")), str(row.get("exit_date", ""))),
                    risk_percent=0.0,
                    capital_at_risk=0.0,
                    position_size=float(row.get("quantity", 0.0) or 0.0),
                )
            )

        for row in (backtest_payload or {}).get("closed_trades", []) or []:
            net_profit = float(row.get("net_pnl", 0.0) or 0.0)
            gross_pnl = float(row.get("gross_pnl", 0.0) or 0.0)
            normalized.append(
                TradeRecord(
                    source="backtesting",
                    trade_id=str(row.get("trade_id", row.get("symbol", ""))),
                    strategy_id=str((backtest_payload or {}).get("configuration", {}).get("strategy_id", "backtest")),
                    strategy_name=str((backtest_payload or {}).get("configuration", {}).get("strategy_name", "Backtest Strategy")),
                    symbol=str(row.get("symbol", "")),
                    asset_class="EQUITY",
                    direction=self._normalize_direction(row.get("direction")),
                    entry_date=str(row.get("entry_date", "")),
                    exit_date=str(row.get("exit_date", "")),
                    entry_price=float(row.get("entry_price", 0.0) or 0.0),
                    exit_price=float(row.get("exit_price", 0.0) or 0.0),
                    quantity=float(row.get("quantity", 0.0) or 0.0),
                    gross_profit=max(0.0, gross_pnl),
                    gross_loss=abs(min(0.0, gross_pnl)),
                    costs=float(row.get("costs", 0.0) or 0.0),
                    net_profit=net_profit,
                    exit_reason=self._normalize_exit_reason(row.get("exit_reason")),
                    holding_hours=self._holding_hours(str(row.get("entry_date", "")), str(row.get("exit_date", ""))),
                    risk_percent=0.0,
                    capital_at_risk=0.0,
                    position_size=float(row.get("quantity", 0.0) or 0.0),
                )
            )

        normalized.sort(key=lambda item: self._dt(item.exit_date) or datetime.min.replace(tzinfo=timezone.utc))
        return normalized

    def _equity_curve_points(self, trades: list[TradeRecord], start_equity: float) -> list[tuple[str, float]]:
        if not trades:
            return [("start", round(start_equity, 2))]

        points: list[tuple[str, float]] = [("start", round(start_equity, 2))]
        running = start_equity
        for trade in trades:
            running += trade.net_profit
            points.append((trade.exit_date or trade.trade_id or "n/a", round(running, 2)))
        return points

    def _drawdown_series(self, equity_points: list[tuple[str, float]]) -> list[tuple[str, float]]:
        peak = 0.0
        rows: list[tuple[str, float]] = []
        for timestamp, equity in equity_points:
            peak = max(peak, float(equity))
            drawdown = 0.0 if peak <= 0 else ((float(equity) - peak) / peak) * 100.0
            rows.append((timestamp, round(drawdown, 2)))
        return rows

    def _portfolio_overview(self, paper_portfolio: dict[str, Any], trades: list[TradeRecord]) -> dict[str, Any]:
        net_profit = sum(item.net_profit for item in trades)
        gross_profit = sum(item.gross_profit for item in trades)
        gross_loss = sum(item.gross_loss for item in trades)
        total_return = (net_profit / self._resolve_starting_equity(paper_portfolio) * 100.0) if self._resolve_starting_equity(paper_portfolio) else 0.0

        return {
            "current_equity": float((paper_portfolio or {}).get("current_equity", (paper_portfolio or {}).get("portfolio_value", 0.0)) or 0.0),
            "portfolio_value": float((paper_portfolio or {}).get("portfolio_value", 0.0) or 0.0),
            "cash": float((paper_portfolio or {}).get("cash", 0.0) or 0.0),
            "buying_power": float((paper_portfolio or {}).get("buying_power", 0.0) or 0.0),
            "open_positions": int((paper_portfolio or {}).get("open_positions", 0) or 0),
            "closed_trades": len(trades),
            "total_return": round(total_return, 2),
            "net_profit": round(net_profit, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss else (float("inf") if gross_profit > 0 else 0.0),
            "expectancy": round(net_profit / len(trades), 2) if trades else 0.0,
            "recovery_factor": 0.0,
            "maximum_drawdown": 0.0,
            "current_drawdown": 0.0,
        }

    def _performance_kpis(self, trades: list[TradeRecord], drawdown_series: list[tuple[str, float]], start_equity: float) -> dict[str, Any]:
        net_profit = sum(item.net_profit for item in trades)
        gross_profit = sum(item.gross_profit for item in trades)
        gross_loss = sum(item.gross_loss for item in trades)
        max_drawdown = min((value for _, value in drawdown_series), default=0.0)
        current_drawdown = drawdown_series[-1][1] if drawdown_series else 0.0
        recovery_factor = (net_profit / abs(max_drawdown)) if max_drawdown < 0 else (net_profit if net_profit > 0 else 0.0)

        return {
            "total_return": round((net_profit / start_equity) * 100.0, 2) if start_equity else 0.0,
            "net_profit": round(net_profit, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss else (float("inf") if gross_profit > 0 else 0.0),
            "expectancy": round(net_profit / len(trades), 2) if trades else 0.0,
            "recovery_factor": round(recovery_factor, 2),
            "maximum_drawdown": round(max_drawdown, 2),
            "current_drawdown": round(current_drawdown, 2),
        }

    def _drawdown_summary(self, drawdown_series: list[tuple[str, float]]) -> dict[str, Any]:
        values = [value for _, value in drawdown_series]
        negative_values = [value for value in values if value < 0]
        durations, recovery_times = self._drawdown_durations(drawdown_series)
        return {
            "current_drawdown": round(values[-1], 2) if values else 0.0,
            "maximum_drawdown": round(min(values), 2) if values else 0.0,
            "average_drawdown": round(mean(negative_values), 2) if negative_values else 0.0,
            "drawdown_duration": max(durations) if durations else 0,
            "recovery_time": round(mean(recovery_times), 2) if recovery_times else 0.0,
        }

    def _trade_analysis(self, trades: list[TradeRecord]) -> dict[str, Any]:
        winners = [item for item in trades if item.net_profit > 0]
        losers = [item for item in trades if item.net_profit < 0]
        holding_hours = [item.holding_hours for item in trades if item.holding_hours >= 0]
        return {
            "total_trades": len(trades),
            "winning_trades": len(winners),
            "losing_trades": len(losers),
            "win_rate": round((len(winners) / len(trades)) * 100.0, 2) if trades else 0.0,
            "loss_rate": round((len(losers) / len(trades)) * 100.0, 2) if trades else 0.0,
            "average_winner": round(mean([item.net_profit for item in winners]), 2) if winners else 0.0,
            "average_loser": round(mean([item.net_profit for item in losers]), 2) if losers else 0.0,
            "largest_winner": round(max([item.net_profit for item in winners]), 2) if winners else 0.0,
            "largest_loser": round(min([item.net_profit for item in losers]), 2) if losers else 0.0,
            "average_holding_time": round(mean(holding_hours), 2) if holding_hours else 0.0,
            "longest_holding_time": round(max(holding_hours), 2) if holding_hours else 0.0,
            "shortest_holding_time": round(min(holding_hours), 2) if holding_hours else 0.0,
        }

    def _exit_analysis(self, trades: list[TradeRecord]) -> list[dict[str, Any]]:
        grouped: dict[str, list[TradeRecord]] = defaultdict(list)
        for trade in trades:
            grouped[trade.exit_reason].append(trade)

        total = len(trades)
        rows = []
        for reason, items in grouped.items():
            rows.append(
                {
                    "exit_reason": reason,
                    "count": len(items),
                    "percentage": round((len(items) / total) * 100.0, 2) if total else 0.0,
                    "net_profit": round(sum(item.net_profit for item in items), 2),
                }
            )
        rows.sort(key=lambda item: item["count"], reverse=True)
        return rows

    def _strategy_analysis(self, trades: list[TradeRecord], start_equity: float) -> list[dict[str, Any]]:
        grouped: dict[str, list[TradeRecord]] = defaultdict(list)
        for trade in trades:
            key = trade.strategy_name or trade.strategy_id or "Unknown"
            grouped[key].append(trade)

        rows = []
        for strategy_name, items in grouped.items():
            net_profit = sum(item.net_profit for item in items)
            wins = [item for item in items if item.net_profit > 0]
            losses = [item for item in items if item.net_profit < 0]
            gross_profit = sum(item.gross_profit for item in items)
            gross_loss = sum(item.gross_loss for item in items)
            points = self._equity_curve_points(items, start_equity)
            drawdown = self._drawdown_series(points)
            rows.append(
                {
                    "strategy_name": strategy_name,
                    "trades": len(items),
                    "win_rate": round((len(wins) / len(items)) * 100.0, 2) if items else 0.0,
                    "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss else (float("inf") if gross_profit > 0 else 0.0),
                    "net_profit": round(net_profit, 2),
                    "average_trade": round(net_profit / len(items), 2) if items else 0.0,
                    "expectancy": round(net_profit / len(items), 2) if items else 0.0,
                    "maximum_drawdown": round(min([value for _, value in drawdown], default=0.0), 2),
                    "average_holding_time": round(mean([item.holding_hours for item in items]), 2) if items else 0.0,
                    "total_return": round((net_profit / start_equity) * 100.0, 2) if start_equity else 0.0,
                }
            )

        rows.sort(key=lambda row: (row["net_profit"], row["profit_factor"], row["win_rate"]), reverse=True)
        for index, row in enumerate(rows, start=1):
            row["rank"] = index
        return rows

    def _time_analysis(self, trades: list[TradeRecord]) -> dict[str, Any]:
        month_profit: dict[str, float] = defaultdict(float)
        dow_profit: dict[str, float] = defaultdict(float)
        hour_profit: dict[int, float] = defaultdict(float)

        for trade in trades:
            exit_dt = self._dt(trade.exit_date)
            if exit_dt is None:
                continue
            month_profit[exit_dt.strftime("%Y-%m")] += trade.net_profit
            dow_profit[exit_dt.strftime("%A")] += trade.net_profit
            hour_profit[int(exit_dt.hour)] += trade.net_profit

        monthly_returns = [
            {"month": month, "net_profit": round(value, 2)}
            for month, value in sorted(month_profit.items())
        ]

        best_month = max(monthly_returns, key=lambda row: row["net_profit"], default={"month": "N/A", "net_profit": 0.0})
        worst_month = min(monthly_returns, key=lambda row: row["net_profit"], default={"month": "N/A", "net_profit": 0.0})

        dow_rows = [{"day": day, "net_profit": round(value, 2)} for day, value in dow_profit.items()]
        best_day = max(dow_rows, key=lambda row: row["net_profit"], default={"day": "N/A", "net_profit": 0.0})
        worst_day = min(dow_rows, key=lambda row: row["net_profit"], default={"day": "N/A", "net_profit": 0.0})

        best_hour = max(hour_profit.items(), key=lambda row: row[1], default=(-1, 0.0))

        return {
            "best_month": best_month,
            "worst_month": worst_month,
            "monthly_returns": monthly_returns,
            "best_day_of_week": best_day,
            "worst_day_of_week": worst_day,
            "best_hour": {"hour": best_hour[0], "net_profit": round(best_hour[1], 2)} if best_hour[0] >= 0 else {"hour": "N/A", "net_profit": 0.0},
        }

    def _long_short_analysis(self, trades: list[TradeRecord]) -> dict[str, Any]:
        def pack(items: list[TradeRecord]) -> dict[str, Any]:
            wins = [item for item in items if item.net_profit > 0]
            losses = [item for item in items if item.net_profit < 0]
            gross_profit = sum(item.gross_profit for item in items)
            gross_loss = sum(item.gross_loss for item in items)
            return {
                "trades": len(items),
                "win_rate": round((len(wins) / len(items)) * 100.0, 2) if items else 0.0,
                "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss else (float("inf") if gross_profit > 0 else 0.0),
                "average_winner": round(mean([item.net_profit for item in wins]), 2) if wins else 0.0,
                "average_loser": round(mean([item.net_profit for item in losses]), 2) if losses else 0.0,
            }

        longs = [item for item in trades if item.direction == "LONG"]
        shorts = [item for item in trades if item.direction == "SHORT"]
        return {
            "long": pack(longs),
            "short": pack(shorts),
        }

    def _asset_analysis(self, trades: list[TradeRecord]) -> list[dict[str, Any]]:
        grouped: dict[str, list[TradeRecord]] = defaultdict(list)
        for trade in trades:
            grouped[(trade.asset_class or "EQUITY").upper()].append(trade)

        rows = []
        for asset_class, items in sorted(grouped.items()):
            rows.append(
                {
                    "asset_class": asset_class,
                    "trades": len(items),
                    "net_profit": round(sum(item.net_profit for item in items), 2),
                    "win_rate": round((len([item for item in items if item.net_profit > 0]) / len(items)) * 100.0, 2) if items else 0.0,
                }
            )
        return rows

    def _risk_analysis(self, trades: list[TradeRecord], paper_portfolio: dict[str, Any]) -> dict[str, Any]:
        risk_values = [item.risk_percent for item in trades if item.risk_percent > 0]
        capital_at_risk = [item.capital_at_risk for item in trades if item.capital_at_risk > 0]
        position_sizes = [item.position_size for item in trades if item.position_size > 0]
        exposure = float((paper_portfolio or {}).get("current_exposure", 0.0) or 0.0)

        return {
            "average_risk": round(mean(risk_values), 2) if risk_values else 0.0,
            "largest_risk": round(max(risk_values), 2) if risk_values else 0.0,
            "capital_at_risk": round(sum(capital_at_risk), 2),
            "average_position_size": round(mean(position_sizes), 2) if position_sizes else 0.0,
            "largest_position": round(max(position_sizes), 2) if position_sizes else 0.0,
            "smallest_position": round(min(position_sizes), 2) if position_sizes else 0.0,
            "exposure": round(exposure, 2),
        }

    def _monthly_return_rows(self, equity_points: list[tuple[str, float]]) -> list[dict[str, Any]]:
        monthly: dict[str, list[float]] = defaultdict(list)
        for timestamp, value in equity_points:
            dt_value = self._dt(timestamp)
            if dt_value is None:
                continue
            monthly[dt_value.strftime("%Y-%m")].append(float(value))

        rows = []
        for month, values in sorted(monthly.items()):
            if not values:
                continue
            start_value = values[0]
            end_value = values[-1]
            ret = 0.0 if start_value == 0 else ((end_value - start_value) / start_value) * 100.0
            rows.append({"month": month, "return_percent": round(ret, 2)})
        return rows

    def _peak_rows(self, equity_points: list[tuple[str, float]]) -> list[dict[str, Any]]:
        peak = 0.0
        rows = []
        for timestamp, value in equity_points:
            peak = max(peak, float(value))
            rows.append({"timestamp": timestamp, "value": round(peak, 2)})
        return rows

    def _drawdown_durations(self, drawdown_series: list[tuple[str, float]]) -> tuple[list[int], list[int]]:
        durations: list[int] = []
        recoveries: list[int] = []
        current = 0
        for _, value in drawdown_series:
            if value < 0:
                current += 1
            elif current > 0:
                durations.append(current)
                recoveries.append(current)
                current = 0
        if current > 0:
            durations.append(current)
        return durations, recoveries

    def _normalize_direction(self, value: Any) -> str:
        text = str(value or "").strip().upper()
        if text in {"SELL", "SHORT"}:
            return "SHORT"
        return "LONG"

    def _normalize_exit_reason(self, value: Any) -> str:
        text = str(value or "").strip().upper().replace(" ", "_")
        mapping = {
            "MANUAL_EXIT": "Manual Exit",
            "STOP_LOSS": "Stop Loss",
            "TAKE_PROFIT": "Take Profit",
            "STRATEGY_EXIT": "Strategy Exit",
            "END_OF_TEST": "End of Test",
        }
        return mapping.get(text, text.replace("_", " ").title() if text else "Unknown")

    def _holding_hours(self, entry_date: str, exit_date: str) -> float:
        entry_dt = self._dt(entry_date)
        exit_dt = self._dt(exit_date)
        if entry_dt is None or exit_dt is None:
            return 0.0
        seconds = max(0.0, (exit_dt - entry_dt).total_seconds())
        return round(seconds / 3600.0, 2)

    def _dt(self, value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        text = str(value or "").strip()
        if not text or text == "start":
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
