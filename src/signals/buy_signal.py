"""
===========================================================
FTSE Quant Trader V2
BUY Signal Engine
===========================================================
"""

from models.signal import Signal


class BuySignal:

    def __init__(self, config):

        self.config = config

        self.setup_active = False
        self.lowest_low = None

    def scan(self, data):

        signals = []

        oversold = self.config.strategy["oversold"]

        for index, row in data.iterrows():

            rsi = row["RSI"]
            low = row["Low"]

            # ------------------------------------------------
            # Start BUY setup
            # ------------------------------------------------

            if not self.setup_active:

                if rsi < oversold:

                    self.setup_active = True
                    self.lowest_low = low

                    print(f"[BUY] {index} Setup started")
                    print(f"      Lowest Low = {low:.2f}")

            # ------------------------------------------------
            # Update Lowest Low
            # ------------------------------------------------

            else:

                if rsi < oversold:

                    if low < self.lowest_low:

                        self.lowest_low = low

                        print(f"[BUY] {index} Lowest Low Updated -> {low:.2f}")

        return signals