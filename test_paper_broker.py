from brokers.paper_broker import PaperBroker
from portfolio.simulation_account import SimulationAccount
from signals.signal_types import SignalType
from signals.trade_signal import TradeSignal

account = SimulationAccount(100000)

broker = PaperBroker(account)

signal = TradeSignal(
    symbol="RR.L",
    action=SignalType.BUY,
    entry_price=250,
    stop_loss=240,
    take_profit=280,
    strategy="RSI Mean Reversion",
)

position = broker.buy(
    signal=signal,
    quantity=100,
)

print("Position Created")
print("--------------------------")
print(position)

print()

print("Remaining Cash")
print("--------------------------")
print(account.cash)