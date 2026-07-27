"""
===========================================================
TradePilotAI
IG Client Interface
===========================================================

Abstracts communication with IG Markets.

Defines the required methods for:
- Market data retrieval
- Opening positions
- Closing positions
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IGClient(ABC):
    """
    Defines the behaviour required from an IG client.
    """

    @abstractmethod
    def get_historical_prices(
        self,
        epic: str,
        start_date: str,
        end_date: str,
    ):
        """
        Retrieve historical price data.

        Returns:
            Provider-specific market data.
        """

        raise NotImplementedError


    @abstractmethod
    def open_position(
        self,
        epic: str,
        direction: str,
        size: float,
        stop_distance: float | None = None,
        limit_distance: float | None = None,
    ):
        """
        Open a position with IG Markets.

        Args:
            epic:
                IG market identifier.

            direction:
                BUY or SELL.

            size:
                Position size.

            stop_distance:
                Optional stop distance.

            limit_distance:
                Optional profit target distance.
        """

        raise NotImplementedError


    @abstractmethod
    def close_position(
        self,
        deal_id: str,
    ):
        """
        Close an existing IG position.

        Args:
            deal_id:
                IG deal reference.
        """

        raise NotImplementedError