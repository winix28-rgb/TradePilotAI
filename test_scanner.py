from tradepilotai_os.scanner.market_scanner import MarketScanner

scanner = MarketScanner()

results = scanner.scan()

for stock in results:

    print(stock)