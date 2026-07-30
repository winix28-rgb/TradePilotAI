"""Paper broker implementation for the TradePilotAI OS."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from tradepilotai_os.models.execution_report import ExecutionReport
from tradepilotai_os.models.order import Order
from tradepilotai_os.models.portfolio import Portfolio
from tradepilotai_os.models.position import Position
from tradepilotai_os.models.trade import Trade
from .base import Broker, ExecutionResult


class PaperBroker(Broker):
    """A realistic paper-trading broker simulation.

    The broker owns all execution rules such as validation,
    commission handling, slippage, cash updates, and position
    accounting. The models remain data-only containers.
    """

    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
    ) -> None:
        self.portfolio = Portfolio(cash=initial_cash)
        self.executed_trades: list[Trade] = []
        self.execution_reports: list[ExecutionReport] = []
        self.commission = commission
        self.slippage = slippage

    def execute(self, trade: Trade) -> ExecutionResult:
        """Execute a trade proposal as a paper order."""

        if trade.entry_price is None:
            return ExecutionResult(
                success=False,
                message="Trade entry price is required.",
                trade=trade,
            )

        if trade.ticker is None or not str(trade.ticker).strip():
            return ExecutionResult(
                success=False,
                message="Trade symbol is required.",
                trade=trade,
            )

        if trade.quantity is None or trade.quantity <= 0:
            return ExecutionResult(
                success=False,
                message="Quantity must be positive.",
                trade=trade,
            )

        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=str(trade.ticker),
            side=trade.direction.upper(),
            quantity=int(trade.quantity),
            price=float(trade.entry_price),
            order_type="MARKET",
        )

        if order.side not in {"BUY", "SELL"}:
            return ExecutionResult(
                success=False,
                message="Only BUY and SELL orders are supported.",
                trade=trade,
            )

        filled_price = self._apply_slippage(order.price or 0.0)
        commission_cost = self.commission * order.quantity
        total_cost = (filled_price * order.quantity) + commission_cost

        if order.side == "BUY":
            if self.portfolio.cash < total_cost:
                return ExecutionResult(
                    success=False,
                    message="Insufficient cash for order.",
                    trade=trade,
                )
            self.portfolio.cash -= total_cost
            self._apply_buy(order, filled_price, commission_cost)
        else:
            self._apply_sell(order, filled_price, commission_cost)

        report = ExecutionReport(
            order=order,
            success=True,
            message="Order executed successfully.",
            filled_price=filled_price,
            filled_quantity=order.quantity,
            metadata={"commission": commission_cost, "slippage": self.slippage},
        )
        self.execution_reports.append(report)
        self.executed_trades.append(trade)

        return ExecutionResult(
            success=True,
            message="Trade executed via paper broker.",
            trade=trade,
            metadata={
                "broker": "paper",
                "execution_report": report,
                "portfolio": self.portfolio,
            },
        )

    def _apply_buy(self, order: Order, fill_price: float, commission_cost: float) -> None:
        """Apply the effect of a buy order to the simulated portfolio."""

        position = self.portfolio.positions.get(order.symbol)
        if position is None:
            position = Position(symbol=order.symbol)
            self.portfolio.positions[order.symbol] = position

        position.quantity += order.quantity
        position.average_price = (
            (position.average_price * (position.quantity - order.quantity))
            + (fill_price * order.quantity)
        ) / position.quantity
        position.market_price = fill_price
        position.exposure = position.quantity * fill_price
        self._update_equity()

    def _apply_sell(self, order: Order, fill_price: float, commission_cost: float) -> None:
        """Apply the effect of a sell order to the simulated portfolio."""

        position = self.portfolio.positions.get(order.symbol)
        if position is None or position.quantity <= 0:
            return

        if order.quantity > position.quantity:
            order.quantity = position.quantity

        realised_pnl = (fill_price - position.average_price) * order.quantity
        self.portfolio.realised_pnl += realised_pnl
        self.portfolio.cash += (fill_price * order.quantity) - commission_cost

        position.quantity -= order.quantity
        if position.quantity == 0:
            position.average_price = 0.0
            position.exposure = 0.0
            position.market_price = 0.0
        else:
            position.market_price = fill_price
            position.exposure = position.quantity * fill_price

        self._update_equity()

    def _apply_slippage(self, price: float) -> float:
        """Apply configurable slippage to the execution price."""

        if self.slippage <= 0:
            return price
        return price * (1 + self.slippage)

    def _update_equity(self) -> None:
        """Recalculate portfolio equity-related metrics."""

        total_exposure = sum(position.exposure for position in self.portfolio.positions.values())
        self.portfolio.exposure = total_exposure
        self.portfolio.unrealised_pnl = 0.0
        for position in self.portfolio.positions.values():
            if position.quantity > 0 and position.average_price > 0:
                self.portfolio.unrealised_pnl += (
                    (position.market_price - position.average_price) * position.quantity
                )
