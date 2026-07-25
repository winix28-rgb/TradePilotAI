"""
===========================================================
TradePilotAI
Backtest Engine
===========================================================

Runs a trading strategy over historical market data.
"""

from __future__ import annotations

from analytics.portfolio_analytics import PortfolioAnalytics
from backtesting.backtest_result import BacktestResult
from backtesting.historical_data import HistoricalData
from core.trade_engine import TradeEngine
from models.trade_order import TradeOrder
from signals.trade_signal import TradeSignal
from strategies.strategy import Strategy


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
        strategy: Strategy,
        historical_data: HistoricalData,
    ) -> BacktestResult:
        """
        Run a strategy across the supplied historical data.
        """

        for index in range(len(historical_data)):

            signal = strategy.generate_signal(
                symbol=symbol,
                historical_data=historical_data,
                index=index,
            )

            if signal is None:
                continue

            order = self._create_order(signal)

            self.trade_engine.execute(order)

        portfolio = self.trade_engine.portfolio

        analytics = PortfolioAnalytics(portfolio)

        return BacktestResult(
            portfolio=portfolio,
            analytics=analytics,
            start_date=historical_data.first.timestamp,
            end_date=historical_data.last.timestamp,
            initial_cash=portfolio.account.buying_power,
            final_value=portfolio.total_value,
        )

    def _create_order(
        self,
        signal: TradeSignal,
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