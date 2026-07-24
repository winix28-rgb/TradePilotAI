"""
===========================================================
TradePilotAI
Simulation Account
===========================================================

Represents a simulated trading account.
"""

from portfolio.account import Account


class SimulationAccount(Account):
    """
    Simple simulated trading account.
    """

    def __init__(self, starting_cash: float):

        if starting_cash < 0:
            raise ValueError("Starting cash cannot be negative.")

        self._cash = float(starting_cash)

    @property
    def cash(self) -> float:
        return self._cash

    @property
    def equity(self) -> float:
        return self._cash

    @property
    def buying_power(self) -> float:
        return self._cash

    def deposit(self, amount: float) -> None:

        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self._cash += amount

    def withdraw(self, amount: float) -> None:

        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if amount > self._cash:
            raise ValueError("Insufficient funds.")

        self._cash -= amount