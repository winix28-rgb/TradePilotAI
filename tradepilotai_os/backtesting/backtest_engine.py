"""Backtesting engine for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

import pandas as pd

from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.core.data_engine import DataEngine
from tradepilotai_os.indicators.ema import EMA
from tradepilotai_os.indicators.rsi import RSI
from tradepilotai_os.models.market_status import MarketStatus
from tradepilotai_os.models.signal import Signal
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk.risk_engine import RiskEngine
from tradepilotai_os.scanner.market_scanner import MarketScanner
from tradepilotai_os.signals.signal_engine import SignalEngine
from tradepilotai_os.strategy.strategy_engine import StrategyEngine


class BacktestEngine:
    """Run a trading pipeline over historical market data.

    This engine composes the existing OS components in the same
    sequence used by live trading: scanner -> data engine ->
    indicators -> signals -> strategy -> risk -> portfolio ->
    paper broker.
    """

    def __init__(self) -> None:
        self.scanner = MarketScanner()
        self.data_engine = DataEngine()
        self.signal_engine = SignalEngine()
        self.strategy_engine = StrategyEngine()
        self.risk_engine = RiskEngine()
        self.portfolio = PortfolioManager(initial_cash=100000.0)
        self.broker = PaperBroker()

    def run(self, symbols: list[str] | None = None) -> dict[str, Any]:
        """Execute the backtest pipeline for the provided symbols."""

        watchlist = symbols or self.scanner.get_watchlist()
        results: list[dict[str, Any]] = []

        for symbol in watchlist:
            data = self.data_engine.download_data(symbol, interval="1d", period="180d")
            if data is None:
                continue

            data = data.copy()
            data["EMA12"] = EMA.calculate(data, 12)
            data["EMA26"] = EMA.calculate(data, 26)
            data["RSI"] = RSI.calculate(data, 14)

            signals = self.signal_engine.find_signals(data, symbol)
            for signal in signals:
                strategy, proposed_trades = self.strategy_engine.evaluate_signal(symbol, signal)
                for trade in proposed_trades:
                    risk_assessment = self.risk_engine.assess_trade(trade)
                    if not risk_assessment.permitted:
                        continue
                    self.portfolio.add_trade(trade)
                    execution = self.broker.execute(trade)
                    results.append(
                        {
                            "symbol": symbol,
                            "signal": signal,
                            "risk": risk_assessment,
                            "execution": execution,
                        }
                    )

        return {
            "results": results,
            "portfolio": self.portfolio.state,
            "executed_trades": len(self.broker.executed_trades),
        }
