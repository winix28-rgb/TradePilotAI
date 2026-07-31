from tradepilotai_os.market_data import YahooMarketDataProvider
from tradepilotai_os.indicators.indicator_engine import IndicatorEngine

provider = YahooMarketDataProvider()

data = provider.history("RR")

data = IndicatorEngine.add_indicators(data)

print(
    data[
        [
            "Close",
            "EMA12",
            "EMA26",
            "RSI",
            "EMA_Bullish",
        ]
    ].tail()
)