"""
Tests for the RiskManager.

These tests verify that the RiskManager correctly applies
the portfolio validation rules before an order can be
executed.
"""

from __future__ import annotations

from models.position import Position
from models.trade_order import TradeOrder
from portfolio.portfolio_manager import PortfolioManager
from portfolio.risk_manager import RiskManager
from portfolio.simulation_account import SimulationAccount
from signals.signal_types import SignalType


def create_portfolio(starting_cash: float = 10_000) -> PortfolioManager:
    """
    Create a PortfolioManager backed by a SimulationAccount.
    """
    account = SimulationAccount(starting_cash)
    return PortfolioManager(account)


def create_order(
    *,
    symbol: str = "RR.L",
    quantity: float = 10,
    price: float = 100,
) -> TradeOrder:
    """
    Create a valid TradeOrder for testing.
    """
    return TradeOrder(
        symbol=symbol,
        action=SignalType.BUY,
        quantity=quantity,
        price=price,
        strategy="Unit Test",
    )


def test_valid_order_is_approved() -> None:
    portfolio = create_portfolio()
    manager = RiskManager(portfolio)

    approved, reason = manager.validate(create_order())

    assert approved is True
    assert reason == "Approved"


def test_quantity_must_be_greater_than_zero() -> None:
    portfolio = create_portfolio()
    manager = RiskManager(portfolio)

    approved, reason = manager.validate(create_order(quantity=0))

    assert approved is False
    assert reason == "Quantity must be greater than zero."


def test_price_must_be_greater_than_zero() -> None:
    portfolio = create_portfolio()
    manager = RiskManager(portfolio)

    approved, reason = manager.validate(create_order(price=0))

    assert approved is False
    assert reason == "Price must be greater than zero."


def test_duplicate_position_is_rejected() -> None:
    portfolio = create_portfolio()

    position = Position(
        symbol="RR.L",
        quantity=100,
        entry_price=100,
        current_price=100,
        strategy="Test",
    )

    portfolio.add_position(position)

    manager = RiskManager(portfolio)

    approved, reason = manager.validate(create_order())

    assert approved is False
    assert "already contains position" in reason


def test_insufficient_buying_power_is_rejected() -> None:
    portfolio = create_portfolio(starting_cash=1_000)

    manager = RiskManager(portfolio)

    order = create_order(
        quantity=100,
        price=100,
    )

    approved, reason = manager.validate(order)

    assert approved is False
    assert reason == "Insufficient buying power for this order."