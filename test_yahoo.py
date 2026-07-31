from tradepilotai_os.market_data import YahooMarketDataProvider

provider = YahooMarketDataProvider()

print("Connected:", provider.connected())

print()

print(provider.quote("RR"))

print()

history = provider.history("RR")

print(history.tail())