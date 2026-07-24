"""
===========================================================
TradePilotAI
Position Sizer
===========================================================

Calculates the number of shares to purchase based on
account size, risk per trade and stop-loss distance.
"""

from dataclasses import dataclass
from math import floor


@dataclass(slots=True)
class PositionSizer:
    """
    Percentage Risk Position Sizer.

    Example

    Account Size : £100,000
    Risk         : 1%
    Max Loss     : £1,000

    Entry        : £250
    Stop         : £245

    Risk/Share   : £5

    Position Size = 1000 / 5 = 200 shares
    """

    account_size: float
    risk_per_trade: float = 0.01

    @property
    def maximum_risk(self) -> float:
        """Maximum amount of money to risk on one trade."""
        return self.account_size * self.risk_per_trade

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
    ) -> int:
        """
        Calculate the number of shares that may be purchased.
        """

        risk_per_share = abs(entry_price - stop_price)

        if risk_per_share <= 0:
            return 0

        shares = floor(self.maximum_risk / risk_per_share)

        return max(shares, 0)

    def position_value(
        self,
        shares: int,
        entry_price: float,
    ) -> float:
        """
        Calculate the total value of the position.
        """
        return shares * entry_price