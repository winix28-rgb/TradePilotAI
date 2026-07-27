"""
===========================================================
TradePilotAI
Trading Session
===========================================================

Controls the lifecycle of a trading run.
"""

from __future__ import annotations

from brokers.broker import Broker

from core.trade_engine import TradeEngine
from core.risk_gateway import RiskGateway

from portfolio.portfolio_manager import PortfolioManager



class TradingSession:
    """
    Coordinates a complete trading session.
    """


    def __init__(
        self,
        broker: Broker,
        portfolio: PortfolioManager,
        risk_gateway: RiskGateway,
    ) -> None:

        self._broker = broker

        self._portfolio = portfolio

        self._risk_gateway = risk_gateway

        self._trade_engine = TradeEngine(
            broker=self._broker,
            portfolio=self._portfolio,
            risk_gateway=self._risk_gateway,
        )

        self._running = False



    @property
    def trade_engine(self) -> TradeEngine:
        return self._trade_engine



    @property
    def running(self) -> bool:
        return self._running



    def start(self) -> None:
        """
        Start trading session.
        """

        if self._running:
            raise RuntimeError(
                "Trading session already running."
            )

        self._running = True



    def stop(self) -> None:
        """
        Stop trading session.
        """

        self._running = False



    def execute_signal(
        self,
        order,
    ):
        """
        Execute a strategy signal.
        """

        if not self._running:

            raise RuntimeError(
                "Trading session is not running."
            )


        return self._trade_engine.execute(
            order
        )