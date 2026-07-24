"""
===========================================================
TradePilotAI
Paper Broker
===========================================================

Simulates order execution.
"""

from brokers.broker import Broker
from models.position import Position
from portfolio.simulation_account import SimulationAccount
from signals.trade_signal import TradeSignal


class PaperBroker(Broker):
    """
    Simple paper trading broker.
    """

    def __init__(self, account: SimulationAccount):

        self.account = account

    def buy(
        self,
        signal: TradeSignal,
        quantity: float,
    ) -> Position:

        cost = signal.entry_price * quantity

        self.account.withdraw(cost)

        return Position(
            symbol=signal.symbol,
            quantity=quantity,
            entry_price=signal.entry_price,
            current_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            strategy=signal.strategy,
        )

    def sell(self, symbol: str) -> Position:

        raise NotImplementedError(
            "Sell functionality will be implemented in the next sprint."
        )