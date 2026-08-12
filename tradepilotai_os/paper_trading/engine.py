"""Single source of truth for paper trading state."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from itertools import count
from typing import Any

from tradepilotai_os.broker.base import ExecutionResult
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.risk.risk_engine import RiskAssessment

from .models import ClosedPaperTrade
from .models import PaperPortfolio
from .models import PaperPosition
from .models import PortfolioStatistics


class PaperPortfolioEngine:
    """Own all paper trading state and portfolio transitions."""

    def __init__(self, initial_capital: float = 100000.0) -> None:
        self._portfolio_ids = count(1)
        self._position_ids = count(1)
        self._trade_ids = count(1)
        self._initial_capital = float(initial_capital)
        self.audit_events: list[dict[str, Any]] = []
        self.portfolio = self.create_portfolio()

    def create_portfolio(self, initial_capital: float | None = None) -> PaperPortfolio:
        if initial_capital is not None:
            self._initial_capital = float(initial_capital)

        self.portfolio = PaperPortfolio(
            portfolio_id=f"PF-{next(self._portfolio_ids):04d}",
            created_date=self._utc_now(),
            cash=self._initial_capital,
            buying_power=self._initial_capital,
            portfolio_value=self._initial_capital,
        )
        self._refresh_portfolio()
        self._record_audit_event("Portfolio Created", portfolio_id=self.portfolio.portfolio_id, cash=self.portfolio.cash)
        return self.portfolio

    def get_portfolio(self) -> PaperPortfolio:
        return self.portfolio

    def get_summary(self) -> dict[str, Any]:
        return self._build_summary()

    def get_open_positions(self) -> list[PaperPosition]:
        return list(self.portfolio.open_positions)

    def get_open_position(self, symbol: str) -> PaperPosition | None:
        return self._find_open_position(symbol)

    def get_open_position_by_id(self, position_id: str) -> PaperPosition | None:
        return self._find_open_position_by_id(position_id)

    def get_closed_trades(self) -> list[ClosedPaperTrade]:
        return list(self.portfolio.closed_trades)

    def get_statistics(self) -> PortfolioStatistics:
        return self.portfolio.portfolio_statistics

    def get_audit_events(self) -> list[dict[str, Any]]:
        return list(self.audit_events)

    def record_audit_event(self, event_name: str, **details: Any) -> dict[str, Any]:
        return self._record_audit_event(event_name, **details)

    def refresh_portfolio(self) -> PaperPortfolio:
        self._refresh_portfolio()
        return self.portfolio

    def open_position(
        self,
        *,
        trade: Trade,
        strategy_id: str = "",
        strategy_name: str = "",
        decision_id: str = "",
        risk_assessment: RiskAssessment | None = None,
        execution_result: ExecutionResult | None = None,
        reason: str = "",
    ) -> PaperPosition | None:
        if trade is None:
            return None

        quantity = int(getattr(trade, "quantity", 0) or 0)
        if quantity <= 0:
            return None

        fill_price = self._filled_price(execution_result, trade)
        entry_value = round(fill_price * quantity, 2)
        position_id = f"PP-{next(self._position_ids):04d}"
        risk_amount = 0.0
        if risk_assessment is not None:
            risk_amount = float((risk_assessment.metadata or {}).get("risk_amount", 0.0) or 0.0)

        self._remove_open_position(str(trade.ticker))
        previous_cash = round(self.portfolio.cash, 2)
        position = PaperPosition(
            position_id=position_id,
            symbol=str(trade.ticker),
            strategy_id=str(strategy_id),
            strategy_name=str(strategy_name),
            direction=str(trade.direction).upper(),
            quantity=quantity,
            entry_date=self._timestamp(getattr(trade, "entry_time", None)),
            entry_price=float(fill_price),
            current_price=float(fill_price),
            market_value=entry_value,
            unrealised_pnl=0.0,
            risk=round(risk_amount, 2),
            stop_loss=float(getattr(trade, "stop_loss", 0.0) or 0.0),
            target=float(getattr(trade, "take_profit", 0.0) or 0.0),
            decision_id=str(decision_id),
            status="OPEN",
        )

        broker_portfolio = self._broker_portfolio(execution_result)
        if broker_portfolio is not None and getattr(broker_portfolio, "cash", None) is not None:
            self.portfolio.cash = round(float(broker_portfolio.cash), 2)
        else:
            self._apply_open_cash_effect(position, entry_value, execution_result)

        self.portfolio.open_positions.append(position)
        self._refresh_portfolio()
        self._record_audit_event(
            "Position Opened",
            position_id=position.position_id,
            symbol=position.symbol,
            strategy_id=position.strategy_id,
            strategy_name=position.strategy_name,
            decision_id=position.decision_id,
            quantity=position.quantity,
            entry_price=position.entry_price,
        )
        self._record_audit_event("Cash Updated", previous=previous_cash, current=self.portfolio.cash)
        self._record_audit_event("Buying Power Updated", current=self.portfolio.buying_power)
        self._record_audit_event("Portfolio Statistics Updated", statistics=asdict(self.portfolio.portfolio_statistics))
        return position

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str,
        *,
        costs: float = 0.0,
        commission: float = 0.0,
        spread_cost: float = 0.0,
        slippage_cost: float = 0.0,
        exit_explanation: str = "",
        exit_date: str | None = None,
    ) -> ClosedPaperTrade | None:
        position = self._find_open_position(symbol)
        if position is None:
            return None

        exit_price = float(exit_price)
        commission = round(float(commission or 0.0), 2)
        spread_cost = round(float(spread_cost or 0.0), 2)
        slippage_cost = round(float(slippage_cost or 0.0), 2)
        additional_costs = round(float(costs or 0.0), 2)
        total_costs = round(commission + spread_cost + slippage_cost + additional_costs, 2)
        gross_profit = self._calculate_gross_profit(position, exit_price)
        net_profit = round(gross_profit - total_costs, 2)
        self._apply_close_cash_effect(position, exit_price, total_costs)
        holding_period_days = self._holding_period_days(position.entry_date, exit_date)

        closed = ClosedPaperTrade(
            trade_id=f"PT-{next(self._trade_ids):04d}",
            position_id=position.position_id,
            decision_id=position.decision_id,
            strategy_id=position.strategy_id,
            strategy_name=position.strategy_name,
            symbol=position.symbol,
            direction=position.direction,
            entry_date=position.entry_date,
            exit_date=exit_date or self._utc_now(),
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            gross_profit=round(gross_profit, 2),
            commission=commission,
            spread_cost=spread_cost,
            slippage_cost=slippage_cost,
            costs=total_costs,
            net_profit=net_profit,
            exit_reason=str(reason),
            exit_explanation=str(exit_explanation),
            holding_period=f"{holding_period_days} days",
            holding_period_days=holding_period_days,
            strategy=position.strategy_name,
        )

        self.portfolio.open_positions = [item for item in self.portfolio.open_positions if item.position_id != position.position_id]
        self.portfolio.closed_trades.append(closed)
        self._refresh_portfolio()
        self._record_audit_event(
            "Position Closed",
            position_id=position.position_id,
            symbol=position.symbol,
            quantity=position.quantity,
            exit_price=exit_price,
            net_profit=net_profit,
        )
        self._record_audit_event("Cash Updated", current=self.portfolio.cash)
        self._record_audit_event("Buying Power Updated", current=self.portfolio.buying_power)
        self._record_audit_event("Portfolio Statistics Updated", statistics=asdict(self.portfolio.portfolio_statistics))
        return closed

    def update_market_price(self, symbol: str, current_price: float) -> PaperPosition | None:
        position = self._find_open_position(symbol)
        if position is None:
            return None

        position.current_price = float(current_price)
        position.market_value = round(position.current_price * position.quantity, 2)
        position.unrealised_pnl = round(self._calculate_unrealised_profit(position, position.current_price), 2)
        self._refresh_portfolio()
        self._record_audit_event(
            "Price Updated",
            symbol=position.symbol,
            current_price=position.current_price,
            market_value=position.market_value,
            unrealised_pnl=position.unrealised_pnl,
        )
        self._record_audit_event("Portfolio Statistics Updated", statistics=asdict(self.portfolio.portfolio_statistics))
        return position

    def update_all_prices(self, prices: dict[str, float]) -> list[PaperPosition]:
        updated: list[PaperPosition] = []
        for symbol, current_price in (prices or {}).items():
            position = self.update_market_price(symbol, float(current_price))
            if position is not None:
                updated.append(position)
        return updated

    def reset_portfolio(self, initial_capital: float | None = None) -> PaperPortfolio:
        portfolio = self.create_portfolio(initial_capital=initial_capital)
        self._record_audit_event("Portfolio Reset", portfolio_id=portfolio.portfolio_id, cash=portfolio.cash)
        return portfolio

    def sync_execution(
        self,
        *,
        trade: Trade,
        execution_result: ExecutionResult,
        strategy_id: str,
        strategy_name: str,
        decision_id: str,
        reason: str,
        risk_assessment: RiskAssessment | None,
    ) -> PaperPosition | None:
        if not execution_result.success or trade is None:
            return None

        return self.open_position(
            trade=trade,
            strategy_id=str(strategy_id),
            strategy_name=str(strategy_name),
            decision_id=str(decision_id),
            risk_assessment=risk_assessment,
            execution_result=execution_result,
            reason=reason,
        )

    def mark_position(self, symbol: str, current_price: float, todays_pnl: float = 0.0) -> PaperPosition | None:
        position = self.update_market_price(symbol, current_price)
        if position is not None:
            position.unrealised_pnl = round(float(todays_pnl), 2)
            self._refresh_portfolio()
        return position

    def snapshot(self) -> dict[str, Any]:
        summary = self.get_summary()
        portfolio = self.get_portfolio()
        statistics = self.get_statistics()
        open_positions = [asdict(item) for item in self.get_open_positions()]
        closed_trades = [asdict(item) for item in self.get_closed_trades()]

        return {
            "summary": summary,
            "portfolio": asdict(portfolio),
            "open_positions": open_positions,
            "closed_trades": closed_trades,
            "statistics": asdict(statistics),
            "portfolio_statistics": asdict(statistics),
            "trade_history": list(closed_trades),
            "audit_events": list(self.audit_events),
        }

    def _record_audit_event(self, event_name: str, **details: Any) -> dict[str, Any]:
        event = {
            "event": event_name,
            "timestamp": self._utc_now(),
            "portfolio_id": self.portfolio.portfolio_id,
            "details": details,
        }
        self.audit_events.append(event)
        return event

    def _refresh_portfolio(self) -> None:
        invested_capital = round(sum(item.market_value for item in self.portfolio.open_positions), 2)
        realised_pnl = round(sum(item.net_profit for item in self.portfolio.closed_trades), 2)
        unrealised_pnl = round(sum(item.unrealised_pnl for item in self.portfolio.open_positions), 2)
        total_pnl = round(realised_pnl + unrealised_pnl, 2)
        self.portfolio.realised_pnl = realised_pnl
        self.portfolio.unrealised_pnl = unrealised_pnl
        self.portfolio.total_pnl = total_pnl
        self.portfolio.buying_power = round(self.portfolio.cash, 2)
        self.portfolio.portfolio_value = round(self.portfolio.cash + invested_capital, 2)
        self.portfolio.portfolio_statistics = self._build_statistics(invested_capital)

    def _build_statistics(self, invested_capital: float) -> PortfolioStatistics:
        closed = list(self.portfolio.closed_trades)
        total_trades = len(closed)
        winning = [item.net_profit for item in closed if item.net_profit > 0]
        losing = [item.net_profit for item in closed if item.net_profit < 0]
        portfolio_value = self.portfolio.portfolio_value or 0.0
        current_exposure = round(sum(item.market_value for item in self.portfolio.open_positions), 2)
        open_position_values = [item.market_value for item in self.portfolio.open_positions]
        open_position_count = len(open_position_values)
        portfolio_return_percent = round((self.portfolio.total_pnl / self._initial_capital) * 100.0, 2) if self._initial_capital else 0.0
        open_position_winners = [item.unrealised_pnl for item in self.portfolio.open_positions if item.unrealised_pnl > 0]
        open_position_losers = [item.unrealised_pnl for item in self.portfolio.open_positions if item.unrealised_pnl < 0]
        winner_candidates = winning + open_position_winners
        loser_candidates = losing + open_position_losers

        return PortfolioStatistics(
            total_trades=total_trades,
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=round((len(winning) / total_trades) * 100.0, 2) if total_trades else 0.0,
            average_winner=round(sum(winning) / len(winning), 2) if winning else 0.0,
            average_loser=round(sum(losing) / len(losing), 2) if losing else 0.0,
            largest_winner=round(max(winner_candidates), 2) if winner_candidates else 0.0,
            largest_loser=round(min(loser_candidates), 2) if loser_candidates else 0.0,
            current_exposure=current_exposure,
            cash_allocation=round((self.portfolio.cash / portfolio_value) * 100.0, 2) if portfolio_value else 0.0,
            invested_allocation=round((invested_capital / portfolio_value) * 100.0, 2) if portfolio_value else 0.0,
            portfolio_return_percent=portfolio_return_percent,
            average_position_size=round(sum(open_position_values) / open_position_count, 2) if open_position_count else 0.0,
            largest_position=round(max(open_position_values), 2) if open_position_values else 0.0,
            smallest_position=round(min(open_position_values), 2) if open_position_values else 0.0,
        )

    def _build_summary(self) -> dict[str, Any]:
        return {
            "portfolio_id": self.portfolio.portfolio_id,
            "created_date": self.portfolio.created_date,
            "cash": round(self.portfolio.cash, 2),
            "buying_power": round(self.portfolio.buying_power, 2),
            "portfolio_value": round(self.portfolio.portfolio_value, 2),
            "current_equity": round(self.portfolio.portfolio_value, 2),
            "realised_pnl": round(self.portfolio.realised_pnl, 2),
            "unrealised_pnl": round(self.portfolio.unrealised_pnl, 2),
            "total_pnl": round(self.portfolio.total_pnl, 2),
            "todays_pnl": round(self.portfolio.unrealised_pnl, 2),
            "overall_pnl": round(self.portfolio.total_pnl, 2),
            "open_positions": len(self.portfolio.open_positions),
            "closed_trades": len(self.portfolio.closed_trades),
            "current_exposure": round(sum(item.market_value for item in self.portfolio.open_positions), 2),
        }

    def _filled_price(self, execution_result: ExecutionResult | None, trade: Trade) -> float:
        if execution_result is not None:
            metadata = execution_result.metadata or {}
            report = metadata.get("execution_report")
            if report is not None and getattr(report, "filled_price", None) is not None:
                return float(report.filled_price)
        return float(getattr(trade, "entry_price", 0.0) or 0.0)

    def _apply_open_cash_effect(self, position: PaperPosition, entry_value: float, execution_result: ExecutionResult | None) -> None:
        commission = 0.0
        if execution_result is not None:
            metadata = execution_result.metadata or {}
            commission = float(metadata.get("commission", 0.0) or 0.0)
        if position.direction == "SELL":
            self.portfolio.cash = round(self.portfolio.cash + entry_value - commission, 2)
        else:
            self.portfolio.cash = round(self.portfolio.cash - entry_value - commission, 2)

    def _apply_close_cash_effect(self, position: PaperPosition, exit_price: float, costs: float) -> None:
        exit_value = round(exit_price * position.quantity, 2)
        if position.direction == "SELL":
            self.portfolio.cash = round(self.portfolio.cash - exit_value - costs, 2)
        else:
            self.portfolio.cash = round(self.portfolio.cash + exit_value - costs, 2)

    def _calculate_gross_profit(self, position: PaperPosition, exit_price: float) -> float:
        if position.direction == "SELL":
            return (position.entry_price - exit_price) * position.quantity
        return (exit_price - position.entry_price) * position.quantity

    def _calculate_unrealised_profit(self, position: PaperPosition, current_price: float) -> float:
        if position.direction == "SELL":
            return (position.entry_price - current_price) * position.quantity
        return (current_price - position.entry_price) * position.quantity

    def _find_open_position(self, symbol: str) -> PaperPosition | None:
        for position in self.portfolio.open_positions:
            if position.symbol == symbol:
                return position
        return None

    def _find_open_position_by_id(self, position_id: str) -> PaperPosition | None:
        for position in self.portfolio.open_positions:
            if position.position_id == position_id:
                return position
        return None

    def _remove_open_position(self, symbol: str) -> None:
        self.portfolio.open_positions = [item for item in self.portfolio.open_positions if item.symbol != symbol]

    def _broker_portfolio(self, execution_result: ExecutionResult | None) -> Any:
        if execution_result is None:
            return None
        metadata = execution_result.metadata or {}
        return metadata.get("portfolio")

    def _timestamp(self, value: Any) -> str:
        if isinstance(value, str) and value:
            return value
        if isinstance(value, datetime):
            dt_value = value
            if dt_value.tzinfo is None:
                dt_value = dt_value.replace(tzinfo=timezone.utc)
            return dt_value.astimezone(timezone.utc).isoformat(timespec="seconds")
        return self._utc_now()

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _holding_period_days(self, entry_date: str, exit_date: str | None) -> int:
        try:
            entry_dt = datetime.fromisoformat(str(entry_date))
            exit_dt = datetime.fromisoformat(str(exit_date)) if exit_date else datetime.now(timezone.utc)
        except ValueError:
            return 0

        if entry_dt.tzinfo is None:
            entry_dt = entry_dt.replace(tzinfo=timezone.utc)
        if exit_dt.tzinfo is None:
            exit_dt = exit_dt.replace(tzinfo=timezone.utc)
        return max(0, (exit_dt.astimezone(timezone.utc) - entry_dt.astimezone(timezone.utc)).days)