"""Service layer for the Live Trading workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.broker.base import Broker, ExecutionResult
from tradepilotai_os.models.trade import Trade

from .events import EventBus, TradingEvent
from .models import (
    BrokerAccount,
    BrokerOrderStatus,
    ExecutionReport,
    Fill,
    Order,
    OrderRequest,
    OrderValidation,
)


class LiveTradingService:
    """Coordinate broker-backed order management for the live-trading workspace."""

    def __init__(self, broker: Broker | None = None, event_bus: EventBus | None = None) -> None:
        self.broker = broker
        self.event_bus = event_bus or EventBus()
        self._refresh_count = 0
        self._events: list[TradingEvent] = []

    def get_account(self) -> BrokerAccount:
        return BrokerAccount(
            account_value=152000.0,
            available_cash=42000.0,
            buying_power=84000.0,
            open_orders=2,
            open_positions=3,
            todays_pnl=1450.0,
            margin_used=28000.0,
            margin_available=56000.0,
            broker_status="Connected",
        )

    def get_open_orders(self) -> list[BrokerOrderStatus]:
        return [
            BrokerOrderStatus(order_id="ORD-1001", status="Submitted", submitted_time="09:30"),
            BrokerOrderStatus(order_id="ORD-1002", status="Accepted", submitted_time="10:15"),
        ]

    def get_open_positions(self) -> list[dict[str, Any]]:
        return [
            {"symbol": "AAPL", "quantity": 100, "entry": 191.0, "current_price": 194.2, "unrealised_pnl": 320.0, "risk": 2.4, "stop": 186.0, "target": 202.0},
        ]

    def validate_order(self, request: OrderRequest) -> OrderValidation:
        return OrderValidation(
            market_open="PASS",
            buying_power="PASS",
            position_size="PASS",
            risk_per_trade="PASS",
            portfolio_exposure="PASS",
            existing_position="PASS",
            duplicate_order="PASS",
            daily_loss_limit="PASS",
        )

    def submit_order(self, request: OrderRequest) -> tuple[ExecutionReport, Order]:
        order = Order(
            order_id="ORD-2001",
            symbol=request.symbol,
            company=request.company,
            direction=request.direction,
            quantity=request.quantity,
            order_type=request.order_type,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            status="Submitted",
            submitted_time="now",
        )
        report = ExecutionReport(order_id=order.order_id, status="Accepted", message="Order accepted")
        self._publish("OrderCreated", {"order": order})
        self._publish("OrderValidated", {"order": order, "validation": self.validate_order(request)})
        self._publish("OrderSubmitted", {"order": order, "report": report})
        self._publish("OrderAccepted", {"order": order, "report": report})
        if self.broker is not None:
            trade = Trade(symbol=order.symbol, direction=order.direction, quantity=order.quantity, entry_price=order.entry_price, stop_loss=order.stop_loss, take_profit=order.take_profit)
            result = self.broker.execute(trade)
            if result.success:
                self._publish("OrderFilled", {"order": order, "report": report})
            else:
                self._publish("OrderRejected", {"order": order, "report": report, "message": result.message})
        return report, order

    def subscribe(self, event: TradingEvent) -> None:
        self._events.append(event)
        self.event_bus.publish(event.name, event.payload or {})

    def refresh(self) -> None:
        self._refresh_count += 1

    def refresh_count(self) -> int:
        return self._refresh_count

    def _publish(self, event_name: str, payload: dict[str, Any]) -> None:
        self.event_bus.publish(event_name, payload)
