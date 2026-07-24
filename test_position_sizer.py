from portfolio.position_sizer import PositionSizer

sizer = PositionSizer(
    account_size=100000,
    risk_per_trade=0.01,
)

shares = sizer.calculate_position_size(
    entry_price=250,
    stop_price=245,
)

print(f"Maximum Risk : £{sizer.maximum_risk:,.2f}")
print(f"Shares        : {shares}")
print(f"Position Size : £{sizer.position_value(shares, 250):,.2f}")