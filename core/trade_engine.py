"""
===========================================================
TradePilotAI
Trade Engine
===========================================================

Coordinates the execution of approved trade orders.

All orders can optionally pass through the Risk Gateway
before reaching the broker.
"""

from __future__ import annotations

from brokers.broker import Broker

from core.risk_gateway import RiskGateway

from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder

from portfolio.portfolio_manager import PortfolioManager

from signals.signal_types import SignalType


class TradeEngine:
    """
    Coordinates order execution.
    """

    def __init__(
        self,
        broker: Broker,
        portfolio: PortfolioManager,
        risk_gateway: RiskGateway | None = None,
    ) -> None:

        self._broker = broker

        self._portfolio = portfolio

        self._risk_gateway = risk_gateway


    @property
    def broker(self) -> Broker:
        """
        Return active broker.
        """

        return self._broker


    @property
    def portfolio(self) -> PortfolioManager:
        """
        Return portfolio manager.
        """

        return self._portfolio


    @property
    def risk_gateway(self) -> RiskGateway | None:
        """
        Return risk gateway.
        """

        return self._risk_gateway


    def execute(
        self,
        order: TradeOrder,
    ) -> Position | Trade:
        """
        Execute a trade order.
        """


        if not isinstance(
            order,
            TradeOrder,
        ):

            raise TypeError(
                "execute() expects a TradeOrder."
            )


        # --------------------------------------------------
        # Risk Gateway
        # --------------------------------------------------

        if self._risk_gateway is not None:

            approved, reason = (
                self._risk_gateway.approve_trade(

                    current_balance=(
                        self.portfolio.account.cash
                    ),

                    current_positions=(
                        len(
                            self.portfolio.positions
                        )
                    ),
                )
            )


            if not approved:

                raise PermissionError(
                    f"Trade rejected: {reason}"
                )


        # --------------------------------------------------
        # BUY
        # --------------------------------------------------

        if order.action == SignalType.BUY:

            position = self.broker.execute(
                order
            )


            self.portfolio.add_position(
                position
            )


            return position



        # --------------------------------------------------
        # SELL
        # --------------------------------------------------

        if order.action == SignalType.SELL:

            position = (
                self.portfolio.get_position(
                    order.symbol
                )
            )


            if position is None:

                raise ValueError(
                    f"No open position exists for {order.symbol}."
                )


            trade = self.broker.execute(
                order,
                position,
            )


            self.portfolio.remove_position(
                order.symbol
            )


            self.portfolio.record_trade(
                trade
            )


            return trade



        raise ValueError(
            f"Unsupported order action: {order.action}"
        )