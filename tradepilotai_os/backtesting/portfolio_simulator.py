"""Portfolio simulation helpers for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.models.portfolio import Portfolio
from tradepilotai_os.models.position import Position
from tradepilotai_os.models.trade import Trade

from .result import BacktestTradeRecord
from .trade_simulator import ExitSimulation
from .trade_simulator import OpenTradeState


class PortfolioSimulator:
    """Track simulated cash, positions, and equity through a backtest."""

    def __init__(self, initial_cash: float = 100000.0) -> None:
        self.initial_cash = float(initial_cash)
        self.portfolio = Portfolio(cash=float(initial_cash), metadata={"initial_cash": float(initial_cash)})
        self.open_trades: dict[str, OpenTradeState] = {}
        self.closed_trades: list[BacktestTradeRecord] = []
        self.equity_curve: list[tuple[Any, float]] = []

    def open_trade(self, state: OpenTradeState) -> None:
        """Apply the cash and position impact of a new trade."""

        trade = state.trade

        quantity = max(1, int(trade.quantity))
        signed_quantity = quantity if trade.direction == "BUY" else -quantity

        if trade.direction == "BUY":
            self.portfolio.cash -= trade.entry_price * quantity
        else:
            self.portfolio.cash += trade.entry_price * quantity

        self.portfolio.cash -= state.entry_commission

        self.portfolio.positions[trade.ticker] = Position(
            symbol=trade.ticker,
            quantity=signed_quantity,
            average_price=trade.entry_price,
            market_price=trade.entry_price,
            exposure=abs(trade.entry_price * quantity),
            metadata={"direction": trade.direction, "entry_time": trade.entry_time},
        )
        self.open_trades[trade.ticker] = state
        self._recalculate()

    def close_trade(self, state: OpenTradeState, exit: ExitSimulation, exit_time: Any) -> BacktestTradeRecord:
        """Close an existing trade and realize its PnL."""

        trade = state.trade

        quantity = max(1, int(trade.quantity))
        exit_price = float(exit.exit_fill_price)

        if trade.direction == "BUY":
            self.portfolio.cash += exit_price * quantity
            profit = (exit.reference_exit_price - state.reference_entry_price) * quantity
        else:
            self.portfolio.cash -= exit_price * quantity
            profit = (state.reference_entry_price - exit.reference_exit_price) * quantity

        self.portfolio.cash -= exit.exit_commission

        trade.exit_time = exit_time
        trade.exit_price = exit_price
        trade.exit_reason = exit.exit_reason
        trade.profit = round(profit - (state.entry_commission + exit.exit_commission + state.entry_spread_cost + exit.exit_spread_cost + state.entry_slippage_cost + exit.exit_slippage_cost), 2)
        trade.status = "CLOSED"

        self.portfolio.realised_pnl += trade.profit or 0.0
        record = BacktestTradeRecord(
            symbol=trade.ticker,
            direction="Long" if trade.direction == "BUY" else "Short",
            entry_date=trade.entry_time,
            entry_price=state.entry_fill_price,
            exit_date=exit_time,
            exit_price=exit_price,
            quantity=quantity,
            gross_pnl=round(profit, 2),
            costs=round(state.entry_commission + exit.exit_commission + state.entry_spread_cost + exit.exit_spread_cost + state.entry_slippage_cost + exit.exit_slippage_cost, 2),
            net_pnl=trade.profit or 0.0,
            exit_reason=exit.exit_reason,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            commission=round(state.entry_commission + exit.exit_commission, 2),
            spread_cost=round(state.entry_spread_cost + exit.exit_spread_cost, 2),
            slippage_cost=round(state.entry_slippage_cost + exit.exit_slippage_cost, 2),
            reference_entry_price=state.reference_entry_price,
            reference_exit_price=exit.reference_exit_price,
        )
        self.closed_trades.append(record)
        self.open_trades.pop(trade.ticker, None)
        self.portfolio.positions.pop(trade.ticker, None)
        if not self.portfolio.positions:
            self.portfolio.unrealised_pnl = 0.0
        self._recalculate()
        return record

    def mark_to_market(self, prices: dict[str, float]) -> None:
        """Update unrealised PnL based on the latest market prices."""

        unrealised = 0.0
        exposure = 0.0

        for symbol, position in self.portfolio.positions.items():
            price = float(prices.get(symbol, position.market_price or position.average_price))
            position.market_price = price
            quantity = abs(position.quantity)
            exposure += abs(price * quantity)
            if position.quantity >= 0:
                unrealised += (price - position.average_price) * quantity
            else:
                unrealised += (position.average_price - price) * quantity

        self.portfolio.unrealised_pnl = round(unrealised, 2)
        self.portfolio.exposure = round(exposure, 2)

    def record_equity_point(self, timestamp: Any, price_or_prices: float | dict[str, float]) -> None:
        """Append an equity point after marking the portfolio to market."""

        if isinstance(price_or_prices, dict):
            self.mark_to_market(price_or_prices)
        else:
            prices = {symbol: float(price_or_prices) for symbol in self.portfolio.positions}
            if prices:
                self.mark_to_market(prices)

        self.equity_curve.append((timestamp, self.equity_value()))

    def equity_value(self) -> float:
        """Return the current total equity."""

        return round(self.portfolio.cash + self.portfolio.unrealised_pnl, 2)

    def _recalculate(self) -> None:
        self.portfolio.exposure = round(sum(abs(position.market_price * abs(position.quantity)) for position in self.portfolio.positions.values()), 2)