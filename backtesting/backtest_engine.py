"""
===========================================================
TradePilotAI
Backtest Engine
===========================================================

Runs a trading strategy over historical market data.

Supports:

- Legacy strategies using generate_signal()
- Production strategies using on_bar()
- Indicator enriched strategy bars
- Risk based position sizing
- Fixed quantity mode for backwards compatibility
"""

from __future__ import annotations

from analytics.portfolio_analytics import PortfolioAnalytics

from backtesting.backtest_result import BacktestResult
from backtesting.equity_point import EquityPoint
from backtesting.historical_data import HistoricalData

from core.trade_engine import TradeEngine

from indicators.indicator_engine import IndicatorEngine

from models.risk_config import RiskConfig
from models.trade_order import TradeOrder

from portfolio.position_sizer import PositionSizer
from portfolio.risk_manager import RiskManager


class BacktestEngine:
    """
    Executes a strategy over historical data.

    Modes:

    Default:
        BacktestEngine(trade_engine)

        Uses default quantity = 100

    Fixed quantity:
        BacktestEngine(
            trade_engine,
            quantity=250
        )

    Risk based:
        BacktestEngine(
            trade_engine,
            risk_config=RiskConfig()
        )
    """

    def __init__(
        self,
        trade_engine: TradeEngine,
        risk_config: RiskConfig | None = None,
        quantity: float | None = None,
    ) -> None:

        # Maintain backwards compatibility
        if risk_config is None and quantity is None:
            quantity = 100.0

        if quantity is not None and quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero."
            )

        self._trade_engine = trade_engine
        self._risk_config = risk_config
        self._quantity = quantity


    @property
    def trade_engine(self) -> TradeEngine:
        return self._trade_engine


    @property
    def quantity(self) -> float | None:
        return self._quantity


    @property
    def risk_config(self) -> RiskConfig | None:
        return self._risk_config


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


        bars = None


        # Production strategies use indicators

        if hasattr(strategy, "on_bar"):

            indicator_engine = IndicatorEngine(

                ema_fast=strategy.config.ema_fast,

                ema_slow=strategy.config.ema_slow,

                rsi_period=strategy.config.rsi_period,
            )


            bars = indicator_engine.calculate(
                historical_data.candles
            )


        equity_curve: list[EquityPoint] = []


        for index in range(len(historical_data)):


            if bars is not None:

                current = bars[index]

                if index > 0:
                    previous = bars[index - 1]

                else:
                    previous = current

            else:

                current = None
                previous = None


            signal = self._generate_signal(

                strategy=strategy,

                symbol=symbol,

                historical_data=historical_data,

                previous=previous,

                current=current,

                index=index,
            )


            if signal is not None:

                if hasattr(signal, "symbol"):

                    order = self._create_order(
                        signal
                    )


                    if self._approve_order(order):

                        self.trade_engine.execute(
                            order
                        )


            equity_curve.append(

                EquityPoint(

                    timestamp=historical_data[index].timestamp,

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
        Support both strategy interfaces.
        """

        if hasattr(strategy, "on_bar"):

            return strategy.on_bar(
                previous,
                current,
            )


        if hasattr(strategy, "generate_signal"):

            return strategy.generate_signal(
                symbol=symbol,
                historical_data=historical_data,
                index=index,
            )


        raise TypeError(
            "Strategy must implement on_bar() or generate_signal()."
        )


    def _approve_order(
        self,
        order: TradeOrder,
    ) -> bool:
        """
        Apply risk validation when enabled.
        """

        if self.risk_config is None:

            return True


        risk_manager = RiskManager(
            self.trade_engine.portfolio
        )


        approved, _ = risk_manager.validate(
            order
        )


        return approved


    def _create_order(
        self,
        signal,
    ) -> TradeOrder:
        """
        Convert strategy signal into order.
        """

        quantity = self._calculate_quantity(
            signal
        )


        return TradeOrder(

            symbol=signal.symbol,

            action=signal.action,

            quantity=quantity,

            price=signal.entry_price,

            stop_loss=signal.stop_loss,

            take_profit=signal.take_profit,

            strategy=signal.strategy,

            timestamp=signal.timestamp,
        )


    def _calculate_quantity(
        self,
        signal,
    ) -> float:
        """
        Calculate position size.

        Fixed quantity mode:
            Uses configured quantity.

        Risk mode:
            Uses portfolio value and stop loss.
        """

        if self.risk_config is None:

            return self.quantity


        portfolio_value = (
            self.trade_engine.portfolio.total_value
        )


        position_sizer = PositionSizer(

            account_size=portfolio_value,

            risk_per_trade=(
                self.risk_config.risk_per_trade
                /
                100
            ),
        )


        return position_sizer.calculate_position_size(

            entry_price=signal.entry_price,

            stop_price=signal.stop_loss,
        )