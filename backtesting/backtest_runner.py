"""
===========================================================
TradePilotAI
Backtest Runner
===========================================================

Creates and coordinates all components required to run a
configuration-driven backtest.
"""

from __future__ import annotations

from backtesting.backtest_engine import BacktestEngine
from backtesting.historical_data import HistoricalData

from brokers.paper_broker import PaperBroker

from core.trade_engine import TradeEngine

from models.application_config import ApplicationConfig

from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount

from strategies.rsi_mean_reversion import (
    RSIMeanReversionStrategy,
)


class BacktestRunner:
    """
    Builds the trading environment from configuration.
    """

    def __init__(
        self,
        config: ApplicationConfig,
    ):
        self.config = config


    def run(
        self,
        symbol: str,
        historical_data: HistoricalData,
    ):
        """
        Run a backtest using the configured strategy.
        """

        strategy = RSIMeanReversionStrategy(
            self.config.strategy
        )

        return self.run_with_strategy(
            symbol=symbol,
            strategy=strategy,
            historical_data=historical_data,
        )


    def run_with_strategy(
        self,
        symbol: str,
        strategy,
        historical_data: HistoricalData,
    ):
        """
        Run a backtest using a supplied strategy.

        Used by the optimisation engine where different
        StrategyConfig values create different strategies.
        """

        account = SimulationAccount(
            self.config.backtest.starting_cash
        )


        portfolio = PortfolioManager(
            account
        )


        broker = PaperBroker(
            account
        )


        trade_engine = TradeEngine(
            broker,
            portfolio
        )


        engine = BacktestEngine(
            trade_engine
        )


        return engine.run(
            symbol=symbol,
            strategy=strategy,
            historical_data=historical_data,
        )