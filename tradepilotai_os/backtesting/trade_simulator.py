"""Trade simulation helpers for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tradepilotai_os.models.trade import Trade
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.risk.risk_engine import RiskEngine

from .result import BacktestTradeRecord


@dataclass(slots=True)
class OpenTradeState:
    """In-flight simulated trade with execution details."""

    trade: Trade
    reference_entry_price: float
    entry_fill_price: float
    entry_commission: float
    entry_spread_cost: float
    entry_slippage_cost: float


@dataclass(slots=True)
class ExitSimulation:
    """Resolved exit details for an open trade."""

    reference_exit_price: float
    exit_fill_price: float
    exit_commission: float
    exit_spread_cost: float
    exit_slippage_cost: float
    exit_reason: str


class TradeSimulator:
    """Convert strategy signals into simulated trade lifecycle events."""

    def __init__(
        self,
        commission_rate: float = 0.0005,
        bid_ask_spread: float = 0.02,
        slippage: float = 0.01,
        risk_engine: RiskEngine | None = None,
    ) -> None:
        self.commission_rate = max(0.0, float(commission_rate))
        self.bid_ask_spread = max(0.0, float(bid_ask_spread))
        self.slippage = max(0.0, float(slippage))
        self.risk_engine = risk_engine

    def open_trade(
        self,
        signal: TradeSignal,
        entry_time: Any,
        quantity: int | None = None,
    ) -> OpenTradeState | None:
        """Create an opening trade from a strategy signal.

        When a risk engine is available, use it for sizing rather than
        duplicating the risk logic here.
        """

        direction = signal.signal.upper()
        if direction not in {"BUY", "SELL"}:
            return None

        reference_entry_price = float(signal.price)
        planned_trade = Trade(
            ticker=signal.symbol,
            direction=direction,
            entry_time=entry_time,
            entry_price=reference_entry_price,
            stop_loss=float(signal.stop_loss),
            quantity=max(1, int(quantity or 1)),
            take_profit=float(signal.target),
            status="OPEN",
        )

        if self.risk_engine is not None and hasattr(self.risk_engine, "assess_trade"):
            assessment = self.risk_engine.assess_trade(planned_trade)
            if not getattr(assessment, "permitted", False):
                return None
            planned_trade.quantity = max(1, int(getattr(assessment, "position_size", planned_trade.quantity) or planned_trade.quantity))
            if getattr(assessment, "stop_loss", None) is not None:
                planned_trade.stop_loss = float(assessment.stop_loss)
            if getattr(assessment, "take_profit", None) is not None:
                planned_trade.take_profit = float(assessment.take_profit)

        entry_fill_price = self._entry_fill_price(reference_entry_price, direction)
        entry_commission = self._commission(entry_fill_price, planned_trade.quantity)
        entry_spread_cost = (self.bid_ask_spread / 2.0) * planned_trade.quantity
        entry_slippage_cost = self.slippage * planned_trade.quantity

        planned_trade.entry_price = entry_fill_price
        return OpenTradeState(
            trade=planned_trade,
            reference_entry_price=reference_entry_price,
            entry_fill_price=entry_fill_price,
            entry_commission=entry_commission,
            entry_spread_cost=entry_spread_cost,
            entry_slippage_cost=entry_slippage_cost,
        )

    def resolve_exit(self, state: OpenTradeState, row: Any, signal: TradeSignal) -> ExitSimulation | None:
        """Resolve stop-loss, take-profit, strategy, or end-of-test exits."""

        trade = state.trade
        reference_close = self._value(row, "Close", trade.entry_price)
        high_price = self._value(row, "High", reference_close)
        low_price = self._value(row, "Low", reference_close)

        if trade.direction == "BUY":
            if low_price <= trade.stop_loss:
                return self._build_exit(state, float(trade.stop_loss), "Stop")
            if trade.take_profit is not None and high_price >= trade.take_profit:
                return self._build_exit(state, float(trade.take_profit), "Target")
        else:
            if high_price >= trade.stop_loss:
                return self._build_exit(state, float(trade.stop_loss), "Stop")
            if trade.take_profit is not None and low_price <= trade.take_profit:
                return self._build_exit(state, float(trade.take_profit), "Target")

        if self.is_opposite_signal(trade, signal):
            return self._build_exit(state, float(reference_close), "Strategy Exit")

        return None

    def build_exit(self, state: OpenTradeState, reference_exit_price: float, exit_reason: str) -> ExitSimulation:
        """Build a concrete exit simulation for the supplied reference price."""

        return self._build_exit(state, float(reference_exit_price), exit_reason)

    def end_of_test_exit(self, state: OpenTradeState, exit_time: Any, reference_exit_price: float) -> BacktestTradeRecord:
        """Finalize an open trade at the end of the backtest."""

        return self.close_trade(state, self.build_exit(state, reference_exit_price, "End of Test"), exit_time)

    def close_trade(
        self,
        state: OpenTradeState,
        exit: ExitSimulation,
        exit_time: Any,
    ) -> BacktestTradeRecord:
        """Finalize a trade and compute lifecycle P/L and execution costs."""

        trade = state.trade
        trade.exit_time = exit_time
        trade.exit_price = exit.exit_fill_price
        trade.exit_reason = exit.exit_reason
        trade.status = "CLOSED"

        quantity = max(1, int(trade.quantity))
        if trade.direction == "BUY":
            gross_pnl = (exit.reference_exit_price - state.reference_entry_price) * quantity
        else:
            gross_pnl = (state.reference_entry_price - exit.reference_exit_price) * quantity

        total_costs = round(
            state.entry_commission
            + exit.exit_commission
            + state.entry_spread_cost
            + exit.exit_spread_cost
            + state.entry_slippage_cost
            + exit.exit_slippage_cost,
            2,
        )
        net_pnl = round(gross_pnl - total_costs, 2)

        trade.profit = net_pnl
        return BacktestTradeRecord(
            symbol=trade.ticker,
            direction="Long" if trade.direction == "BUY" else "Short",
            entry_date=trade.entry_time,
            entry_price=state.entry_fill_price,
            exit_date=exit_time,
            exit_price=exit.exit_fill_price,
            quantity=quantity,
            gross_pnl=round(gross_pnl, 2),
            costs=total_costs,
            net_pnl=net_pnl,
            exit_reason=exit.exit_reason,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            commission=round(state.entry_commission + exit.exit_commission, 2),
            spread_cost=round(state.entry_spread_cost + exit.exit_spread_cost, 2),
            slippage_cost=round(state.entry_slippage_cost + exit.exit_slippage_cost, 2),
            reference_entry_price=state.reference_entry_price,
            reference_exit_price=exit.reference_exit_price,
        )

    def is_opposite_signal(self, trade: Trade, signal: TradeSignal) -> bool:
        """Return True when the new signal conflicts with the open trade direction."""

        direction = signal.signal.upper()
        return (trade.direction == "BUY" and direction == "SELL") or (trade.direction == "SELL" and direction == "BUY")

    def _value(self, row: Any, column: str, default: float) -> float:
        try:
            if isinstance(row, dict):
                return float(row.get(column, default))
            return float(row[column])
        except Exception:
            return float(default)

    def _commission(self, price: float, quantity: int) -> float:
        return round(abs(price) * max(1, int(quantity)) * self.commission_rate, 2)

    def _entry_fill_price(self, reference_price: float, direction: str) -> float:
        if direction == "BUY":
            return round(reference_price + (self.bid_ask_spread / 2.0) + self.slippage, 2)
        return round(reference_price - (self.bid_ask_spread / 2.0) - self.slippage, 2)

    def _exit_fill_price(self, reference_price: float, direction: str) -> float:
        if direction == "BUY":
            return round(reference_price - (self.bid_ask_spread / 2.0) - self.slippage, 2)
        return round(reference_price + (self.bid_ask_spread / 2.0) + self.slippage, 2)

    def _build_exit(self, state: OpenTradeState, reference_exit_price: float, exit_reason: str) -> ExitSimulation:
        direction = state.trade.direction
        exit_fill_price = self._exit_fill_price(reference_exit_price, direction)
        exit_commission = self._commission(exit_fill_price, state.trade.quantity)
        exit_spread_cost = (self.bid_ask_spread / 2.0) * state.trade.quantity
        exit_slippage_cost = self.slippage * state.trade.quantity
        return ExitSimulation(
            reference_exit_price=round(reference_exit_price, 2),
            exit_fill_price=exit_fill_price,
            exit_commission=exit_commission,
            exit_spread_cost=exit_spread_cost,
            exit_slippage_cost=exit_slippage_cost,
            exit_reason=exit_reason,
        )