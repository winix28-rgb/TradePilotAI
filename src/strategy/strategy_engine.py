"""
===========================================================
FTSE Quant Trader V2
Strategy Engine
===========================================================

Maintains an independent strategy state for every ticker.
Processes market data one candle at a time.
"""

from models.strategy_state import StrategyState
from models.trade import Trade
from signals.signal_engine import SignalEngine


class StrategyEngine:

    def __init__(self):
        self.strategies = {}
        self.signal_engine = SignalEngine()


    def get_strategy(self, ticker):
        """
        Return the StrategyState for a ticker.
        Create one if it doesn't already exist.
        """

        if ticker not in self.strategies:
            self.strategies[ticker] = StrategyState()

        return self.strategies[ticker]

    def reset_strategy(self, strategy):
        """
        Reset the strategy after a trade or invalid setup.
        """

        strategy.state = StrategyState.IDLE
        strategy.lowest_low = None
        strategy.highest_high = None
        strategy.entry_price = None
        strategy.stop_loss = None
        strategy.entry_index = None
        strategy.entry_time = None

        # Reset the setup age counter
        strategy.setup_age = 0
     

    def evaluate(self, ticker, prices):
        """
        Evaluate one ticker.

        Returns:
            StrategyState
            list[Trade]
        """

        strategy = self.get_strategy(ticker)

        completed_trades = []

        for i in range(1, len(prices) - 1):

            previous = prices.iloc[i - 1]
            current = prices.iloc[i]
            next_candle = prices.iloc[i + 1]

            rsi = float(current["RSI"])
            low = float(current["Low"])
            close = float(current["Close"])

            # =====================================================
            # IDLE
            # =====================================================

            if strategy.state == StrategyState.IDLE:

                if rsi < 30:
                    strategy.state = StrategyState.WATCHING_LONG
                    strategy.lowest_low = low
                    strategy.setup_age = 0

            # =====================================================
            # WATCHING LONG
            # =====================================================

            elif strategy.state == StrategyState.WATCHING_LONG:

                if low < strategy.lowest_low:
                    strategy.lowest_low = low

                if rsi > 30:
                    strategy.state = StrategyState.READY_TO_BUY
                    strategy.setup_age = 0

            # =====================================================
            # READY TO BUY
            # =====================================================

            elif strategy.state == StrategyState.READY_TO_BUY:

                strategy.setup_age += 1

                # Cancel stale setups
                if strategy.setup_age > 10:

                    print(
                        f"[TIMEOUT] {ticker} "
                        f"Setup expired after {strategy.setup_age} candles."
                    )

                    self.reset_strategy(strategy)
                    continue

                # RSI became oversold again, start a fresh setup
                if rsi < 30:

                    print(
                        f"[RESET] {ticker} "
                        "RSI dropped below 30 again."
                    )

                    strategy.state = StrategyState.WATCHING_LONG
                    strategy.lowest_low = low
                    strategy.setup_age = 0
                    continue

                if self.signal_engine.is_bullish_crossover(previous, current):

                    strategy.state = StrategyState.LONG

                    strategy.entry_price = float(next_candle["Open"])
                    strategy.stop_loss = strategy.lowest_low
                    strategy.entry_index = i + 1
                    strategy.entry_time = next_candle.name


                    print("\n" + "=" * 70)
                    print(f"DEBUG ENTRY : {ticker}")
                    print("=" * 70)

                    print("\nPrevious Candle")
                    print(previous[["Open", "High", "Low", "Close", "EMA12", "EMA26", "RSI"]])

                    print("\nCurrent Candle")
                    print(current[["Open", "High", "Low", "Close", "EMA12", "EMA26", "RSI"]])

                    print("\nNext Candle")
                    print(next_candle[["Open", "High", "Low", "Close", "EMA12", "EMA26", "RSI"]])

                    print(f"\nStored Lowest Low : {strategy.lowest_low:.2f}")
                    print(f"Entry Price       : {strategy.entry_price:.2f}")
                    print(f"Stop Loss         : {strategy.stop_loss:.2f}")

                    #
                    # Validate the setup
                    #

                    if strategy.stop_loss >= strategy.entry_price:

                        print("\n*** INVALID LONG SETUP DETECTED ***")
                        print("Trade skipped because the stop loss is not below the entry price.")
                        print("=" * 70)

                        self.reset_strategy(strategy)
                        continue

                    print("=" * 70)

                    strategy.state = StrategyState.LONG

                    print(
                        f"[BUY ] {ticker}"
                        f" Entry={strategy.entry_price:.2f}"
                        f" Stop={strategy.stop_loss:.2f}"
                    )

            # =====================================================
            # LONG
            # =====================================================
           
            elif strategy.state == StrategyState.LONG:

                #
                # Stop Loss
                #

                if low <= strategy.stop_loss:

                    trade = Trade(
                        ticker=ticker,
                        direction="LONG",
                        entry_time=strategy.entry_time,
                        entry_price=strategy.entry_price,
                        stop_loss=strategy.stop_loss,
                        exit_time=current.name,
                        exit_price=strategy.stop_loss,
                        exit_reason="STOP LOSS",
                        profit=strategy.stop_loss - strategy.entry_price,
                        status="CLOSED",
                    )

                    completed_trades.append(trade)

                    print(
                        f"[STOP] {ticker}"
                        f" Exit={trade.exit_price:.2f}"
                        f" Profit={trade.profit:.2f}"
                    )

                    self.reset_strategy(strategy)

                #
                # RSI Exit
                #
                elif rsi >= 50:

                    trade = Trade(
                        ticker=ticker,
                        direction="LONG",
                        entry_time=strategy.entry_time,
                        entry_price=strategy.entry_price,
                        stop_loss=strategy.stop_loss,
                        exit_time=current.name,
                        exit_price=close,
                        exit_reason="RSI 50",
                        profit=close - strategy.entry_price,
                        status="CLOSED",
                    )

                    completed_trades.append(trade)

                    print(
                        f"[EXIT] {ticker}"
                        f" Exit={trade.exit_price:.2f}"
                        f" Profit={trade.profit:.2f}"
                    )

                    self.reset_strategy(strategy)

        return strategy, completed_trades

    def print_all_states(self):
        """
        Display the strategy state for every ticker.
        """

        print()
        print("=" * 60)
        print("STRATEGY STATES")
        print("=" * 60)

        for ticker, strategy in self.strategies.items():
            print(f"{ticker:8} {strategy.state}")