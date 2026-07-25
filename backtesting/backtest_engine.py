"""
===========================================================
TradePilotAI
Backtest Engine
===========================================================

Runs a trading strategy over historical market data.

Supports:
- Legacy strategies using generate_signal()
- Production strategies using on_bar()
"""

from __future__ import annotations

from analytics.portfolio_analytics import PortfolioAnalytics
from backtesting.backtest_result import BacktestResult
from backtesting.equity_point import EquityPoint
from backtesting.historical_data import HistoricalData
from core.trade_engine import TradeEngine
from models.trade_order import TradeOrder


class BacktestEngine:
    """
    Executes a strategy over historical data.
    """

    def __init__(
        self,
        trade_engine: TradeEngine,
        quantity: float = 100.0,
    ) -> None:

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero."
            )

        self._trade_engine = trade_engine
        self._quantity = quantity


    @property
    def trade_engine(self) -> TradeEngine:
        return self._trade_engine


    @property
    def quantity(self) -> float:
        return self._quantity


    def run(
        self,
        symbol: str,
        strategy,
        historical_data: HistoricalData,
    ) -> BacktestResult:
        """
        Run a strategy across historical data.
        """

        portfolio = self.trade_engine.portfolio

        starting_cash = portfolio.account.cash

        equity_curve: list[EquityPoint] = []


        for index in range(len(historical_data)):

            candle = historical_data[index]

            current = self._create_strategy_bar(
                candle
            )


            if index > 0:

                previous = self._create_strategy_bar(
                    historical_data[index - 1]
                )

            else:

                previous = current


            signal = self._generate_signal(
                strategy=strategy,
                symbol=symbol,
                historical_data=historical_data,
                previous=previous,
                current=current,
                index=index,
            )


            # ------------------------------------------------
            # Only create an order when a real TradeSignal
            # exists.
            #
            # SignalType.NONE is ignored.
            # ------------------------------------------------

            if signal is not None:

                if hasattr(signal, "symbol"):

                    order = self._create_order(
                        signal
                    )

                    self.trade_engine.execute(
                        order
                    )


            equity_curve.append(
                EquityPoint(
                    timestamp=candle.timestamp,
                    equity=portfolio.total_value,
                )
            )


        analytics = PortfolioAnalytics(
            portfolio
        )


        return BacktestResult(
            portfolio=portfolio,
            analytics=analytics,
            start_date=historical_data.first.timestamp,
            end_date=historical_data.last.timestamp,
            initial_cash=starting_cash,
            final_value=portfolio.total_value,
            equity_curve=equity_curve,
        )


    def _generate_signal(
        self,
        strategy,
        symbol,
        historical_data,
        previous,
        current,
        index,
    ):
        """
        Supports both strategy architectures.
        """

        # New production strategy interface

        if hasattr(strategy, "on_bar"):

            return strategy.on_bar(
                previous,
                current,
            )


        # Legacy strategy interface

        if hasattr(strategy, "generate_signal"):

            return strategy.generate_signal(
                symbol=symbol,
                historical_data=historical_data,
                index=index,
            )


        raise TypeError(
            "Strategy must implement on_bar() or generate_signal()."
        )


    def _create_strategy_bar(
        self,
        candle,
    ):
        """
        Convert Candle into strategy-compatible data.

        Indicator values are temporary placeholders.
        The indicator pipeline will replace these later.
        """

        return {
            "Open": candle.open,
            "High": candle.high,
            "Low": candle.low,
            "Close": candle.close,
            "Volume": candle.volume,

            "RSI": 50,

            "EMA12": candle.close,

            "EMA26": candle.close,
        }


    def _create_order(
        self,
        signal,
    ) -> TradeOrder:

        return TradeOrder(
            symbol=signal.symbol,
            action=signal.action,
            quantity=self.quantity,
            price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            strategy=signal.strategy,
            timestamp=signal.timestamp,
        )