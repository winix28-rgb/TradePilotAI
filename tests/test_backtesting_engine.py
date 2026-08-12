from __future__ import annotations

import pandas as pd
import pytest

from tradepilotai_os.backtesting import BacktestEngine, BacktestResult, PerformanceEngine, PortfolioSimulator, TradeSimulator
from tradepilotai_os.backtesting.strategy_library import StrategyLibraryEngine
from tradepilotai_os.backtesting.strategy_library.strategies import RSIMeanReversionBacktestStrategy
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.risk.risk_engine import RiskEngine


class StubStrategyEngine:
    def evaluate(self, symbol: str, data):
        if len(data) == 30:
            return TradeSignal(
                symbol=symbol,
                signal="BUY",
                confidence=85,
                price=float(data.iloc[-1]["Close"]),
                rsi=25.0,
                ema12=101.0,
                ema26=102.0,
                stop_loss=float(data.iloc[-1]["Close"]) - 5.0,
                target=float(data.iloc[-1]["Close"]) + 10.0,
                reasons=["oversold", "bullish"],
            )
        if len(data) == 35:
            return TradeSignal(
                symbol=symbol,
                signal="SELL",
                confidence=85,
                price=float(data.iloc[-1]["Close"]),
                rsi=75.0,
                ema12=99.0,
                ema26=98.0,
                stop_loss=float(data.iloc[-1]["Close"]) + 5.0,
                target=float(data.iloc[-1]["Close"]) - 10.0,
                reasons=["overbought", "bearish"],
            )
        return TradeSignal(
            symbol=symbol,
            signal="HOLD",
            confidence=40,
            price=float(data.iloc[-1]["Close"]),
            rsi=50.0,
            ema12=100.0,
            ema26=100.0,
            stop_loss=float(data.iloc[-1]["Close"]) - 5.0,
            target=float(data.iloc[-1]["Close"]) + 10.0,
            reasons=["neutral"],
        )

class CostAwareStrategyEngine:
    def evaluate(self, symbol: str, data):
        close = float(data.iloc[-1]["Close"])
        if len(data) == 30:
            return TradeSignal(
                symbol=symbol,
                signal="BUY",
                confidence=90,
                price=close,
                rsi=25.0,
                ema12=101.0,
                ema26=99.0,
                stop_loss=98.0,
                target=112.0,
                reasons=["oversold", "bullish"],
            )
        return TradeSignal(
            symbol=symbol,
            signal="HOLD",
            confidence=45,
            price=close,
            rsi=50.0,
            ema12=100.0,
            ema26=100.0,
            stop_loss=98.0,
            target=112.0,
            reasons=["neutral"],
        )

class RiskSizingStrategyEngine:
    def evaluate(self, symbol: str, data):
        close = float(data.iloc[-1]["Close"])
        if len(data) == 30:
            return TradeSignal(
                symbol=symbol,
                signal="BUY",
                confidence=90,
                price=close,
                rsi=25.0,
                ema12=101.0,
                ema26=99.0,
                stop_loss=95.0,
                target=110.0,
                reasons=["oversold", "bullish"],
            )
        return TradeSignal(
            symbol=symbol,
            signal="HOLD",
            confidence=45,
            price=close,
            rsi=50.0,
            ema12=100.0,
            ema26=100.0,
            stop_loss=95.0,
            target=110.0,
            reasons=["neutral"],
        )


class TimeframeRecordingDataEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def download_data(self, ticker: str, interval: str, period: str):
        self.calls.append((ticker, interval, period))
        return _build_frame()

def _build_frame(high_value: float = 112.5) -> pd.DataFrame:
    closes = [100.0 + (index * 0.1) for index in range(40)]
    highs = [price + 0.5 for price in closes]
    lows = [price - 0.5 for price in closes]
    for index in range(30, 40):
        highs[index] = high_value
        lows[index] = 99.0
    return pd.DataFrame(
        {
            "Close": closes,
            "High": highs,
            "Low": lows,
        },
        index=pd.date_range("2025-01-01", periods=40, freq="D"),
    )

def test_backtest_engine_applies_commission_spread_slippage_and_net_pl():
    frame = _build_frame()

    simulator = TradeSimulator(commission_rate=0.01, bid_ask_spread=1.0, slippage=0.5)
    engine = BacktestEngine(
        strategy_engine=CostAwareStrategyEngine(),
        portfolio_simulator=PortfolioSimulator(initial_cash=10000.0),
        trade_simulator=simulator,
        performance_engine=PerformanceEngine(),
    )

    result = engine.run_backtest(market_data={"AAPL": frame})

    assert isinstance(result, BacktestResult)
    assert len(result.closed_trades) == 1

    trade = result.closed_trades[0]
    assert trade.symbol == "AAPL"
    assert trade.direction == "Long"
    assert trade.exit_reason == "Target"
    assert trade.quantity == 1
    assert trade.entry_date is not None
    assert trade.exit_date is not None
    assert trade.exit_date > trade.entry_date
    assert trade.reference_entry_price is not None
    assert trade.reference_exit_price is not None
    assert trade.entry_price == pytest.approx(trade.reference_entry_price + 1.0)
    assert trade.exit_price == pytest.approx(trade.reference_exit_price - 1.0)
    expected_gross = trade.reference_exit_price - trade.reference_entry_price
    expected_commission = (trade.entry_price + trade.exit_price) * 0.01
    expected_spread = 1.0
    expected_slippage = 1.0
    expected_costs = expected_commission + expected_spread + expected_slippage
    expected_net = expected_gross - expected_costs
    assert trade.gross_pnl == pytest.approx(expected_gross)
    assert trade.commission == pytest.approx(expected_commission)
    assert trade.spread_cost == pytest.approx(expected_spread)
    assert trade.slippage_cost == pytest.approx(expected_slippage)
    assert trade.costs == pytest.approx(expected_costs)
    assert trade.net_pnl == pytest.approx(expected_net)

    assert result.metrics["total_trades"] == 1
    assert result.metrics["net_profit"] == pytest.approx(expected_net)
    assert result.metrics["total_return"] == pytest.approx(round(expected_net / 10000.0 * 100.0, 2))
    assert result.portfolio.cash == pytest.approx(10000.0 + expected_net)
    assert result.to_dict()["executed_trades"] == 1
    assert result.to_dict()["summary"]["source"] == "backtest_engine"

def test_backtest_engine_uses_risk_engine_when_available():
    frame = _build_frame(high_value=110.5)
    risk_engine = RiskEngine(account_balance=10000.0, risk_per_trade=0.01, max_position_size=10)

    engine = BacktestEngine(
        strategy_engine=RiskSizingStrategyEngine(),
        portfolio_simulator=PortfolioSimulator(initial_cash=10000.0),
        trade_simulator=TradeSimulator(commission_rate=0.0, bid_ask_spread=0.0, slippage=0.0, risk_engine=risk_engine),
        performance_engine=PerformanceEngine(),
        risk_engine=risk_engine,
    )

    result = engine.run_backtest(market_data={"MSFT": frame})

    assert len(result.closed_trades) == 1
    assert result.closed_trades[0].quantity == 10
    assert result.closed_trades[0].net_pnl == pytest.approx(result.closed_trades[0].gross_pnl)

def test_backtest_engine_consumes_strategy_signals_and_returns_result_model():
    prices = [100.0 + (index * 0.1) for index in range(40)]
    frame = pd.DataFrame(
        {
            "Close": prices,
            "High": [price + 0.5 for price in prices],
            "Low": [price - 0.5 for price in prices],
        },
        index=pd.date_range("2025-01-01", periods=40, freq="D"),
    )

    engine = BacktestEngine(strategy_engine=StubStrategyEngine(), portfolio_simulator=PortfolioSimulator(initial_cash=10000.0), trade_simulator=TradeSimulator(), performance_engine=PerformanceEngine())
    result = engine.run_backtest(market_data={"AAPL": frame})

    assert isinstance(result, BacktestResult)
    assert result.closed_trades
    assert result.metrics["total_trades"] == 1
    assert result.metrics["gross_profit"] != 0
    assert result.symbol_results["AAPL"]["status"] == "completed"
    assert result.to_dict()["executed_trades"] == 1
    assert result.to_dict()["summary"]["source"] == "backtest_engine"


def test_backtest_engine_defaults_to_strategy_primary_timeframe() -> None:
    data_engine = TimeframeRecordingDataEngine()
    engine = BacktestEngine(
        strategy_engine=StrategyLibraryEngine(RSIMeanReversionBacktestStrategy()),
        data_engine=data_engine,
        portfolio_simulator=PortfolioSimulator(initial_cash=10000.0),
        trade_simulator=TradeSimulator(),
        performance_engine=PerformanceEngine(),
    )

    engine.run_backtest(symbols=["AAPL"], interval=None, period="30d")

    assert data_engine.calls[0][1] == "1h"


def test_backtest_engine_honors_user_override_timeframe() -> None:
    data_engine = TimeframeRecordingDataEngine()
    engine = BacktestEngine(
        strategy_engine=StrategyLibraryEngine(RSIMeanReversionBacktestStrategy()),
        data_engine=data_engine,
        portfolio_simulator=PortfolioSimulator(initial_cash=10000.0),
        trade_simulator=TradeSimulator(),
        performance_engine=PerformanceEngine(),
    )

    engine.run_backtest(symbols=["AAPL"], interval="2h", period="30d")

    assert data_engine.calls[0][1] == "2h"