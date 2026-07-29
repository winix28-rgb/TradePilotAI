"""Base service definition."""

from abc import ABC, abstractmethod


class Service(ABC):
    """Base class for all services."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable service name."""

    @abstractmethod
    def start(self) -> None:
        """Start the service."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the service."""