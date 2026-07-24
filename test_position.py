from datetime import datetime

from models.position import Position

position = Position(
    symbol="RR.L",
    entry_date=datetime.now(),
    entry_price=250,
    shares=200,
)

print("Cost:", position.cost)
print("Market Value:", position.market_value(265))
print("Profit:", position.unrealised_profit(265))
print("Return %:", position.unrealised_return(265))