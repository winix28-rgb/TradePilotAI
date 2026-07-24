from portfolio.portfolio_manager import PortfolioManager

portfolio = PortfolioManager(100000)

print(f"Starting Cash : £{portfolio.cash:,.2f}")

portfolio.buy(
    symbol="RR.L",
    shares=200,
    price=250,
)

print(f"Cash After Buy : £{portfolio.cash:,.2f}")

portfolio.sell(
    symbol="RR.L",
    price=265,
)

print(f"Cash After Sell : £{portfolio.cash:,.2f}")

print(f"Portfolio Value : £{portfolio.total_value:,.2f}")