"""
===========================================================
TradePilotAI
Main Application
===========================================================

Application entry point.

Modes:

BACKTEST
PAPER
DEMO
"""

from __future__ import annotations


from backtesting.performance import Performance
from backtesting.statistics import Statistics

from brokers.broker_factory import BrokerFactory

from config.settings import Settings

from core.risk_gateway import RiskGateway
from core.strategy_engine import StrategyEngine
from core.trading_session import TradingSession

from data.data_loader import DataLoader

from indicators.indicator_engine import IndicatorEngine

from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount

from services.account_service import AccountService

from risk.daily_loss_limit import DailyLossLimit
from risk.max_position_manager import MaxPositionManager
from risk.position_reconciler import PositionReconciler
from risk.trading_kill_switch import TradingKillSwitch

from strategies.rsi_mean_reversion import (
    RSIMeanReversionStrategy,
)



# =========================================================
# BACKTEST MODE
# =========================================================

def run_backtest():

    print("=" * 60)
    print("TradePilotAI Backtest")
    print("=" * 60)


    data = DataLoader.load_yahoo(
        "RR.L"
    )


    data = IndicatorEngine.add_indicators(
        data
    )


    strategy = RSIMeanReversionStrategy()


    engine = StrategyEngine(
        strategy
    )


    trades = engine.run(
        data
    )


    stats = Statistics(
        trades
    )


    performance = Performance(
        stats
    )


    print()

    print(
        f"Trades       : {stats.total_trades}"
    )

    print(
        f"Win Rate     : {stats.win_rate:.2f}%"
    )

    print(
        f"Net Profit   : {stats.net_profit:.2f}"
    )

    print(
        f"Profit Factor: {performance.profit_factor:.2f}"
    )



# =========================================================
# CREATE TRADING SESSION
# =========================================================

def create_trading_session(
    settings: Settings,
):

    account = SimulationAccount(
        starting_cash=10000
    )


    portfolio = PortfolioManager(
        account
    )


    broker = BrokerFactory.create(
        settings,
        account,
    )


    risk_gateway = RiskGateway(

        daily_loss_limit=DailyLossLimit(
            starting_balance=account.cash,
            max_loss_percent=2,
        ),

        max_position_manager=MaxPositionManager(
            maximum_positions=10,
        ),

        kill_switch=TradingKillSwitch(),

        position_reconciler=PositionReconciler(),

    )


    return (
        TradingSession(

            broker=broker,

            portfolio=portfolio,

            risk_gateway=risk_gateway,

        ),

        broker,
    )



# =========================================================
# PAPER MODE
# =========================================================

def run_paper_trading(
    settings: Settings,
):

    print("=" * 60)
    print("TradePilotAI PAPER")
    print("=" * 60)


    session, _ = create_trading_session(
        settings
    )


    session.start()


    print(
        "Paper trading session started."
    )


    session.stop()


    print(
        "Paper trading session stopped."
    )



# =========================================================
# IG DEMO MODE
# =========================================================

def run_ig_demo(
    settings: Settings,
):

    print("=" * 60)
    print("TradePilotAI IG DEMO")
    print("=" * 60)


    print(
        "Connecting to IG..."
    )


    session, broker = create_trading_session(
        settings
    )


    print(
        "IG connection successful ✅"
    )


    if hasattr(
        broker,
        "_client",
    ):

        account_service = AccountService(
            broker._client
        )


        summary = (
            account_service.get_account_summary()
        )


        print(
            "Account information retrieved ✅"
        )


        print(summary)


    print(
        "IG DEMO session ready ✅"
    )



# =========================================================
# MAIN
# =========================================================

def main():

    settings = Settings.load()


    print("=" * 60)
    print("TradePilotAI")
    print("=" * 60)


    print(
        f"Mode: {settings.mode}"
    )


    mode = settings.mode.upper()


    if mode == "BACKTEST":

        run_backtest()


    elif mode == "PAPER":

        run_paper_trading(
            settings
        )


    elif mode == "DEMO":

        run_ig_demo(
            settings
        )


    else:

        raise ValueError(
            f"Unsupported mode: {settings.mode}"
        )



if __name__ == "__main__":

    main()