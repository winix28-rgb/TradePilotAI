"""Data provider for the Live Trading workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .service import LiveTradingService


class LiveTradingDataProvider:
    """Resolve live-trading workspace data from the dependency container."""

    def __init__(self, container: Container | None = None, service: LiveTradingService | None = None) -> None:
        self.container = container
        self.service = service

    def get_live_trading_data(self) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            service = self.container.resolve(LiveTradingService)
        if service is None:
            service = LiveTradingService()

        account = service.get_account()
        return {
            "account": self._account_payload(account),
            "orders": [self._order_payload(order) for order in service.get_open_orders()],
            "positions": service.get_open_positions(),
            "validation": self._validation_payload(service.validate_order(self._default_request())),
            "request": self._default_request(),
            "timeline": ["Created", "Validated", "Submitted", "Accepted", "Partially Filled", "Filled", "Closed"],
            "events": [],
        }

    def _default_request(self) -> dict[str, Any]:
        return {
            "symbol": "AAPL",
            "company": "Apple Inc.",
            "direction": "BUY",
            "quantity": 100,
            "order_type": "MARKET",
            "entry_price": 191.0,
            "stop_loss": 186.0,
            "take_profit": 202.0,
            "estimated_risk": 500.0,
            "estimated_reward": 1100.0,
            "risk_reward": "1:2",
            "estimated_margin": 25000.0,
        }

    def _account_payload(self, account: Any) -> dict[str, Any]:
        return {
            "account_value": account.account_value,
            "available_cash": account.available_cash,
            "buying_power": account.buying_power,
            "open_orders": account.open_orders,
            "open_positions": account.open_positions,
            "todays_pnl": account.todays_pnl,
            "margin_used": account.margin_used,
            "margin_available": account.margin_available,
            "broker_status": account.broker_status,
        }

    def _order_payload(self, order: Any) -> dict[str, Any]:
        return {
            "order_id": order.order_id,
            "symbol": order.order_id,
            "order_type": "MARKET",
            "quantity": 100,
            "status": order.status,
            "submitted_time": order.submitted_time,
        }

    def _validation_payload(self, validation: Any) -> dict[str, str]:
        return {
            "market_open": validation.market_open,
            "buying_power": validation.buying_power,
            "position_size": validation.position_size,
            "risk_per_trade": validation.risk_per_trade,
            "portfolio_exposure": validation.portfolio_exposure,
            "existing_position": validation.existing_position,
            "duplicate_order": validation.duplicate_order,
            "daily_loss_limit": validation.daily_loss_limit,
        }
