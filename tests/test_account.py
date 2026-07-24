from portfolio.simulation_account import SimulationAccount

account = SimulationAccount(100000)

print("Initial State")
print("------------------------")
print(f"Cash         : £{account.cash:,.2f}")
print(f"Equity       : £{account.equity:,.2f}")
print(f"Buying Power : £{account.buying_power:,.2f}")

print()

print("Depositing £5,000...")
account.deposit(5000)

print(f"Cash         : £{account.cash:,.2f}")

print()

print("Withdrawing £25,000...")
account.withdraw(25000)

print(f"Cash         : £{account.cash:,.2f}")

print()

print("Attempting to withdraw £1,000,000...")

try:
    account.withdraw(1_000_000)
except ValueError as e:
    print(f"Error: {e}")