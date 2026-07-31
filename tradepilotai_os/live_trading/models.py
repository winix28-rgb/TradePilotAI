"""Domain models for the Live Trading workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Order:
    """Represents a trading order in the live-trading workspace."""

    order_id: str
    symbol: str
    company: str
    direction: str
    quantity: int
    order_type: str = "MARKET"
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    status: str = "Created"
    submitted_time: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderRequest:
    """Represents the order request payload from the ticket form."""

    symbol: str
    company: str
    direction: str
    quantity: int
    order_type: str = "MARKET"
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    estimated_risk: float | None = None
    estimated_reward: float | None = None
    risk_reward: str = "1:2"
    estimated_margin: float | None = None


@dataclass(slots=True)
class OrderValidation:
    """Represents the validation outcome for a proposed order."""

    market_open: str = "PASS"
    buying_power: str = "PASS"
    position_size: str = "PASS"
    risk_per_trade: str = "PASS"
    portfolio_exposure: str = "PASS"
    existing_position: str = "PASS"
    duplicate_order: str = "PASS"
    daily_loss_limit: str = "PASS"


@dataclass(slots=True)
class ExecutionReport:
    """Represents a broker execution report payload."""

    order_id: str
    status: str
    message: str
    filled_quantity: int = 0


@dataclass(slots=True)
class Fill:
    """Represents an execution fill for an order."""

    order_id: str
    quantity: int
    price: float
    timestamp: str


@dataclass(slots=True)
class BrokerAccount:
    """Represents the account state surfaced by the broker interface."""

    account_value: float
    available_cash: float
    buying_power: float
    open_orders: int
    open_positions: int
    todays_pnl: float
    margin_used: float
    margin_available: float
    broker_status: str = "Connected"


@dataclass(slots=True)
class BrokerOrderStatus:
    """Represents the current order state from the broker interface."""

    order_id: str
    status: str
    submitted_time: str | None = None
