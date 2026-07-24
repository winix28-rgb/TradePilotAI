from models.position import Position
from portfolio.portfolio_manager import PortfolioManager
from portfolio.simulation_account import SimulationAccount

account = SimulationAccount(100000)

portfolio = PortfolioManager(account)

position = Position(
    symbol="RR.L",
    quantity=100,
    entry_price=250,
    current_price=250,
)

portfolio.add_position(position)

print("Cash")
print(account.cash)

print()

print("Portfolio Value")
print(portfolio.portfolio_value)

print()

print("Total Value")
print(portfolio.total_value)

print()

print("Updating Price...")

position.update_price(275)

print()

print("Portfolio Value")
print(portfolio.portfolio_value)

print()

print("Total Value")
print(portfolio.total_value)

print()

print("Has RR.L?")
print(portfolio.has_position("RR.L"))