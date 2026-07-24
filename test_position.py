from models.position import Position

position = Position(
    symbol="RR.L",
    quantity=100,
    entry_price=250.00,
    current_price=250.00,
    stop_loss=240.00,
    take_profit=280.00,
    strategy="RSI Mean Reversion",
)

print("Initial Position")
print("------------------------")
print(f"Symbol        : {position.symbol}")
print(f"Quantity      : {position.quantity}")
print(f"Cost          : £{position.cost:,.2f}")
print(f"Market Value  : £{position.market_value:,.2f}")
print(f"Profit/Loss   : £{position.unrealised_profit:,.2f}")
print(f"Return        : {position.unrealised_return:.2f}%")

print()

print("Updating market price to £265...")

position.update_price(265)

print()

print(f"Market Value  : £{position.market_value:,.2f}")
print(f"Profit/Loss   : £{position.unrealised_profit:,.2f}")
print(f"Return        : {position.unrealised_return:.2f}%")