from datetime import datetime

import pytest

from backtesting.backtest_engine import BacktestEngine
from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount
from signals.signal_types import SignalType
from signals.trade_signal import TradeSignal
from strategies.strategy import Strategy


class RecordingTradeEngine:
    """
    Simple fake TradeEngine used for testing.
    """

    def __init__(self):

        account = SimulationAccount(10000)

        self.portfolio = PortfolioManager(account)

        self.orders = []

    def execute(self, order):

        self.orders.append(order)


class CountingStrategy(Strategy):

    def __init__(self):

        self.calls = 0

    def generate_signal(
        self,
        symbol,
        historical_data,
        index,
    ):

        self.calls += 1

        return None


class BuyStrategy(Strategy):

    def generate_signal(
        self,
        symbol,
        historical_data,
        index,
    ):

        if index == 0:

            candle = historical_data[index]

            return TradeSignal(
                symbol=symbol,
                action=SignalType.BUY,
                entry_price=candle.close,
            )

        return None


def sample_history():

    return HistoricalData(
        [
            Candle(
                datetime(2025, 1, 1),
                100,
                105,
                95,
                102,
                1000,
            ),
            Candle(
                datetime(2025, 1, 2),
                102,
                106,
                100,
                104,
                1200,
            ),
        ]
    )


def test_invalid_quantity():

    engine = RecordingTradeEngine()

    with pytest.raises(ValueError):

        BacktestEngine(engine, quantity=0)


def test_strategy_called_for_every_candle():

    strategy = CountingStrategy()

    engine = RecordingTradeEngine()

    backtester = BacktestEngine(engine)

    history = sample_history()

    backtester.run(
        "RR.L",
        strategy,
        history,
    )

    assert strategy.calls == len(history)


def test_no_signal_creates_no_orders():

    strategy = CountingStrategy()

    engine = RecordingTradeEngine()

    backtester = BacktestEngine(engine)

    backtester.run(
        "RR.L",
        strategy,
        sample_history(),
    )

    assert len(engine.orders) == 0


def test_buy_signal_creates_order():

    strategy = BuyStrategy()

    engine = RecordingTradeEngine()

    backtester = BacktestEngine(
        engine,
        quantity=25,
    )

    backtester.run(
        "RR.L",
        strategy,
        sample_history(),
    )

    assert len(engine.orders) == 1

    order = engine.orders[0]

    assert order.symbol == "RR.L"
    assert order.quantity == 25
    assert order.action == SignalType.BUY


def test_result_dates_are_correct():

    strategy = CountingStrategy()

    engine = RecordingTradeEngine()

    backtester = BacktestEngine(engine)

    history = sample_history()

    result = backtester.run(
        "RR.L",
        strategy,
        history,
    )

    assert result.start_date == history.first.timestamp
    assert result.end_date == history.last.timestamp