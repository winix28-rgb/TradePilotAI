from models.trade_order import TradeOrder
from signals.signal_types import SignalType

order = TradeOrder(
    symbol="RR.L",
    action=SignalType.BUY,
    quantity=100,
    price=250,
    stop_loss=240,
    take_profit=280,
    strategy="RSI Mean Reversion",
)

print("Trade Order")
print("----------------------")
print(f"Symbol      : {order.symbol}")
print(f"Action      : {order.action.name}")
print(f"Quantity    : {order.quantity}")
print(f"Price       : £{order.price:.2f}")
print(f"Order Value : £{order.value:,.2f}")