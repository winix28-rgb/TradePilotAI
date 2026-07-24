"""
===========================================================
TradePilotAI
Account Interface
===========================================================

Defines the behaviour of every account implementation.
"""

from abc import ABC, abstractmethod


class Account(ABC):
    """
    Abstract base class for all trading accounts.
    """

    @property
    @abstractmethod
    def cash(self) -> float:
        """Available cash."""
        pass

    @property
    @abstractmethod
    def equity(self) -> float:
        """Current account equity."""
        pass

    @property
    @abstractmethod
    def buying_power(self) -> float:
        """Amount available to trade."""
        pass

    @abstractmethod
    def deposit(self, amount: float) -> None:
        """Add funds to the account."""
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        """Remove funds from the account."""
        pass