"""Strategy decision engine for the TradePilotAI OS."""

from __future__ import annotations

from __future__ import annotations

from tradepilotai_os.models.signal import Signal
from tradepilotai_os.models.strategy_state import StrategyState
from tradepilotai_os.models.trade import Trade


class StrategyEngine:
    """Evaluate standardized signals into trading decisions.

    This layer consumes signal objects and maintains per-symbol
    strategy state. It does not access market data, brokers, or
    portfolio management systems directly.
    """

    def __init__(self) -> None:
        self.strategies: dict[str, StrategyState] = {}

    def get_strategy(self, ticker: str) -> StrategyState:
        """Return the strategy state for a ticker, creating it if needed."""

        if ticker not in self.strategies:
            self.strategies[ticker] = StrategyState()
        return self.strategies[ticker]

    def reset_strategy(self, strategy: StrategyState) -> None:
        """Reset a strategy state after a completed trade or invalid setup."""

        strategy.state = StrategyState.IDLE
        strategy.lowest_low = None
        strategy.highest_high = None
        strategy.entry_price = None
        strategy.stop_loss = None
        strategy.entry_index = None
        strategy.entry_time = None
        strategy.setup_age = 0

    def evaluate_signal(self, ticker: str, signal: Signal) -> tuple[StrategyState, list[Trade]]:
        """Turn a standardized signal into a trading decision."""

        strategy = self.get_strategy(ticker)
        completed_trades: list[Trade] = []

        decision = self._map_signal_to_decision(signal)
        if decision == "BUY":
            strategy.state = StrategyState.LONG
            strategy.entry_price = signal.entry_price
            strategy.stop_loss = signal.stop_loss
            strategy.entry_index = 0
            strategy.entry_time = None

            trade = Trade(
                ticker=ticker,
                direction="BUY",
                entry_time=None,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=self._calculate_take_profit(signal.entry_price, signal.stop_loss, "BUY"),
                exit_time=None,
                exit_price=None,
                exit_reason="SIGNAL",
                profit=None,
                status="OPEN",
            )
            completed_trades.append(trade)
        elif decision == "SELL":
            strategy.state = StrategyState.SHORT
            strategy.entry_price = signal.entry_price
            strategy.stop_loss = signal.stop_loss
            strategy.entry_index = 0
            strategy.entry_time = None

            trade = Trade(
                ticker=ticker,
                direction="SELL",
                entry_time=None,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=self._calculate_take_profit(signal.entry_price, signal.stop_loss, "SELL"),
                exit_time=None,
                exit_price=None,
                exit_reason="SIGNAL",
                profit=None,
                status="OPEN",
            )
            completed_trades.append(trade)
        else:
            strategy.state = StrategyState.IDLE
            strategy.entry_price = None
            strategy.stop_loss = None
            strategy.entry_index = None
            strategy.entry_time = None

        return strategy, completed_trades

    def _map_signal_to_decision(self, signal: Signal) -> str:
        """Translate an EMA/RSI signal into an explicit BUY/SELL/HOLD decision."""

        if signal.signal_type == "BUY" and signal.ema12 > signal.ema26 and signal.rsi >= 50:
            return "BUY"
        if signal.signal_type == "SELL" and signal.ema12 < signal.ema26 and signal.rsi <= 50:
            return "SELL"
        return "HOLD"

    def _calculate_take_profit(self, entry_price: float, stop_loss: float, direction: str) -> float:
        """Compute a simple risk-based take-profit level."""

        distance = abs(entry_price - stop_loss)
        if direction == "BUY":
            return entry_price + (distance * 2)
        return entry_price - (distance * 2)

    def print_all_states(self) -> None:
        """Print the strategy states for all tracked tickers."""

        print()
        print("=" * 60)
        print("STRATEGY STATES")
        print("=" * 60)

        for ticker, strategy in self.strategies.items():
            print(f"{ticker:8} {strategy.state}")
