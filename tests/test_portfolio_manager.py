"""
===========================================================
TradePilotAI
Portfolio Manager Tests
===========================================================
"""

import pytest

from models.position import Position
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount


@pytest.fixture
def portfolio():
    return PortfolioManager(SimulationAccount(100000))


@pytest.fixture
def position():
    return Position(
        symbol="RR.L",
        quantity=100,
        entry_price=250,
        current_price=250,
        stop_loss=240,
        take_profit=280,
        strategy="RSI",
    )


def test_add_position(portfolio, position):
    portfolio.add_position(position)

    assert portfolio.has_position("RR.L")


def test_duplicate_position_raises_error(portfolio, position):
    portfolio.add_position(position)

    with pytest.raises(ValueError):
        portfolio.add_position(position)


def test_remove_position(portfolio, position):
    portfolio.add_position(position)

    removed = portfolio.remove_position("RR.L")

    assert removed.symbol == "RR.L"
    assert not portfolio.has_position("RR.L")


def test_get_position(portfolio, position):
    portfolio.add_position(position)

    assert portfolio.get_position("RR.L") is position


def test_empty_portfolio_value(portfolio):
    assert portfolio.portfolio_value == 0


def test_total_value_equals_cash_when_empty(portfolio):
    assert portfolio.total_value == 100000