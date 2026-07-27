"""
===========================================================
TradePilotAI
Risk Gateway
===========================================================

Central control point for all pre-trade risk checks.
"""

from __future__ import annotations

from risk.daily_loss_limit import DailyLossLimit
from risk.max_position_manager import MaxPositionManager
from risk.trading_kill_switch import TradingKillSwitch
from risk.position_reconciler import PositionReconciler


class RiskGateway:
    """
    Executes all risk checks before allowing trades.
    """

    def __init__(
        self,
        daily_loss_limit: DailyLossLimit,
        max_position_manager: MaxPositionManager,
        kill_switch: TradingKillSwitch,
        position_reconciler: PositionReconciler,
    ) -> None:

        self._daily_loss_limit = daily_loss_limit

        self._max_position_manager = (
            max_position_manager
        )

        self._kill_switch = kill_switch

        self._position_reconciler = (
            position_reconciler
        )


    def approve_trade(
        self,
        current_balance: float,
        current_positions: int,
    ) -> tuple[bool, str]:
        """
        Run all pre-trade checks.
        """


        if not self._kill_switch.trading_allowed():

            return (
                False,
                "Trading disabled by kill switch.",
            )


        if not self._daily_loss_limit.trading_allowed(
            current_balance
        ):

            return (
                False,
                "Daily loss limit exceeded.",
            )


        if not self._max_position_manager.can_open_position(
            current_positions
        ):

            return (
                False,
                "Maximum position limit reached.",
            )


        return (
            True,
            "Approved",
        )