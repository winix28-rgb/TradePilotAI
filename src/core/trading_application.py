"""
===========================================================
FTSE Quant Trader V2
Trading Application
===========================================================
"""

from core.config_manager import ConfigManager
from core.data_engine import DataEngine
from indicators.indicator_engine import IndicatorEngine
from signals.signal_engine import SignalEngine
from scanner.market_scanner import MarketScanner
from strategy.strategy_engine import StrategyEngine


class TradingApplication:
    """
    Main application controller.

    Responsible for coordinating all system components.
    """

    def __init__(self):

        print("=" * 60)
        print("FTSE Quant Trader V2")
        print("=" * 60)

        self.config = ConfigManager()
        self.data_engine = DataEngine()
        self.indicator_engine = IndicatorEngine()
        self.signal_engine = SignalEngine()
        self.strategy_engine = StrategyEngine()
        self.scanner = MarketScanner()

    def run(self):

        print()
        print("Loading strategy configuration...")
        print(f"Timeframe : {self.config.strategy['timeframe']}")
        print(f"EMA Fast  : {self.config.strategy['ema_fast']}")
        print(f"EMA Slow  : {self.config.strategy['ema_slow']}")
        print(f"RSI       : {self.config.strategy['rsi_period']}")

        print()
        print("Scanning market...")

        watchlist = self.scanner.get_watchlist()

        total_signals = 0
        total_completed_trades = 0

        for ticker in watchlist:

            print()
            print("-" * 60)
            print(f"Scanning {ticker}")

            prices = self.data_engine.download_data(
                ticker=ticker,
                interval=self.config.strategy["timeframe"],
                period="180d",
            )

            if prices is None:
                print(f"Failed to download {ticker}")
                continue

            prices = self.indicator_engine.add_indicators(prices)

            status = self.signal_engine.get_market_status(prices, ticker)

            # =====================================================
            # Evaluate Strategy
            # =====================================================

            strategy, completed_trades = self.strategy_engine.evaluate(
                ticker,
                prices
            )

            # =====================================================
            # Market Summary
            # =====================================================

            print(f"Ticker         : {status.ticker}")
            print(f"Trend          : {status.trend}")
            print(f"Current Signal : {status.current_signal}")

            if status.signal_age >= 0:
                print(f"Signal Age     : {status.signal_age} candles")
            else:
                print("Signal Age     : None")

            print(f"Close          : {status.close:.2f}")
            print(f"EMA12          : {status.ema12:.2f}")
            print(f"EMA26          : {status.ema26:.2f}")
            print(f"RSI            : {status.rsi:.2f}")

            print(f"Strategy State : {strategy.state}")

            if strategy.lowest_low is not None:
                print(f"Lowest Low     : {strategy.lowest_low:.2f}")

            # =====================================================
            # Completed Trades
            # =====================================================

            if completed_trades:

                print()
                print("Completed Trades")
                print("----------------")

                for trade in completed_trades:

                    total_completed_trades += 1

                    print(
                        f"{trade.direction:5} "
                        f"Entry {trade.entry_price:8.2f} "
                        f"Exit {trade.exit_price:8.2f} "
                        f"P/L {trade.profit:8.2f} "
                        f"{trade.exit_reason}"
                    )

            if status.current_signal != "NONE":
                total_signals += 1

        print()
        print("=" * 60)
        print(f"TOTAL SIGNALS FOUND : {total_signals}")
        print(f"TOTAL TRADES CLOSED : {total_completed_trades}")
        print("=" * 60)

        self.strategy_engine.print_all_states()

        return total_signals