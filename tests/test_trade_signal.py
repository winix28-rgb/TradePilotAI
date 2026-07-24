from signals.trade_signal import TradeSignal
from signals.signal_types import SignalType

signal = TradeSignal(
    symbol="RR.L",
    action=SignalType.BUY,
    entry_price=250.00,
    stop_loss=245.00,
    take_profit=265.00,
    strategy="RSI Mean Reversion",
)

print(signal)

print(f"Buy Signal : {signal.is_buy}")
print(f"Risk/Share : £{signal.risk_per_share:.2f}")