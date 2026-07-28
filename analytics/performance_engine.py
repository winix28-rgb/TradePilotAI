"""
===========================================================
TradePilotAI
Performance Engine

Advanced trading statistics.
===========================================================
"""

from __future__ import annotations



class PerformanceEngine:
    """
    Calculates trading performance metrics.
    """

    def __init__(
        self,
        trades=None,
    ):

        self.trades = trades or []



    def add_trade(
        self,
        trade,
    ):

        self.trades.append(
            trade
        )



    @property
    def total_trades(self):

        return len(
            self.trades
        )



    @property
    def winning_trades(self):

        return len(

            [
                trade

                for trade in self.trades

                if trade["profit"] > 0

            ]

        )



    @property
    def losing_trades(self):

        return len(

            [
                trade

                for trade in self.trades

                if trade["profit"] < 0

            ]

        )



    @property
    def win_rate(self):

        if self.total_trades == 0:

            return 0


        return (

            self.winning_trades

            /

            self.total_trades

        ) * 100



    @property
    def net_profit(self):

        return sum(

            trade["profit"]

            for trade in self.trades

        )



    @property
    def average_profit(self):

        if self.total_trades == 0:

            return 0


        return (

            self.net_profit

            /

            self.total_trades

        )



    @property
    def gross_profit(self):

        return sum(

            trade["profit"]

            for trade in self.trades

            if trade["profit"] > 0

        )



    @property
    def gross_loss(self):

        return abs(

            sum(

                trade["profit"]

                for trade in self.trades

                if trade["profit"] < 0

            )

        )



    @property
    def profit_factor(self):

        if self.gross_loss == 0:

            return float("inf")


        return (

            self.gross_profit

            /

            self.gross_loss

        )



    @property
    def equity_curve(self):

        """
        Returns account value progression.
        """

        equity = 0

        curve = []


        for trade in self.trades:

            equity += trade["profit"]

            curve.append(
                equity
            )


        return curve



    @property
    def maximum_drawdown(self):

        """
        Calculates largest peak-to-trough decline.
        """

        curve = self.equity_curve


        if not curve:

            return 0


        peak = curve[0]

        max_drawdown = 0


        for value in curve:

            if value > peak:

                peak = value


            drawdown = peak - value


            if drawdown > max_drawdown:

                max_drawdown = drawdown


        return max_drawdown