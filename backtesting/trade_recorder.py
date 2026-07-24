"""
===========================================================
TradePilotAI
Trade Recorder
===========================================================

Purpose
-------
Converts BUY and SELL signals into completed Trade objects.

Responsibilities
----------------
- Open a trade on BUY.
- Close a trade on SELL.
- Store completed trades.

Does NOT
---------
- Generate signals.
- Calculate indicators.
- Manage portfolio.
"""

from models.trade import Trade
from signals.signal_types import SignalType


class TradeRecorder:

    def __init__(self):

        self.current_trade = None
        self.trades = []

    def process_signal(
        self,
        signal,
        date,
        price,
        symbol="RR.L",
    ):

        # -----------------------------
        # BUY
        # -----------------------------

        if signal == SignalType.BUY:

            if self.current_trade is None:

                self.current_trade = {
                    "symbol": symbol,
                    "entry_date": date,
                    "entry_price": float(price),
                }

        # -----------------------------
        # SELL
        # -----------------------------

        elif signal == SignalType.SELL:

            if self.current_trade is not None:

                trade = Trade(
                    symbol=self.current_trade["symbol"],
                    entry_date=self.current_trade["entry_date"],
                    exit_date=date,
                    entry_price=self.current_trade["entry_price"],
                    exit_price=float(price),
                    quantity=1,
                    exit_reason="RSI Exit",
                )

                self.trades.append(trade)

                self.current_trade = None