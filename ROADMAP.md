# TradePilotAI Roadmap

> Long-term development plan for TradePilotAI.

---

# Vision

TradePilotAI aims to become a professional algorithmic trading platform capable of researching, testing and executing systematic trading strategies across multiple markets.

The project is being developed incrementally, with each milestone building on a stable, well-tested foundation.

---

# Development Status

| Milestone | Status |
|-----------|:------:|
| Core Trading Engine | ✅ Complete |
| Complete Trade Lifecycle | 🚧 In Progress |
| Portfolio Analytics | ⏳ Planned |
| Backtesting Engine | ⏳ Planned |
| Live Trading | ⏳ Planned |
| Machine Learning | 🔮 Future |

---

# Milestone 1 – Core Trading Engine ✅

Completed.

### Features

- TradeSignal
- TradeOrder
- Position
- Trade
- PortfolioManager
- SimulationAccount
- Broker Interface
- PaperBroker
- TradeEngine
- Unit Testing
- Clean Architecture

---

# Milestone 2 – Complete Trade Lifecycle 🚧

Current milestone.

### Objectives

- Complete SELL execution
- Remove positions after SELL
- Record completed trades
- Trade history
- Integration testing
- End-to-end trade workflow

Expected Result

```
BUY
 ↓
Position
 ↓
SELL
 ↓
Trade
 ↓
Cash Updated
 ↓
Portfolio Updated
```

---

# Milestone 3 – Portfolio Analytics

### Objectives

- Win Rate
- Total Profit
- Total Loss
- Average Winner
- Average Loser
- Largest Winner
- Largest Loser
- Profit Factor
- Expectancy
- Equity Curve

---

# Milestone 4 – Strategy Framework

### Objectives

- Multiple Strategies
- Strategy Base Class
- Strategy Registry
- Strategy Performance Comparison
- Parameter Optimisation

---

# Milestone 5 – Backtesting Engine

### Objectives

- Historical Data Loader
- Backtest Engine
- Slippage Simulation
- Commission Modelling
- Position Sizing
- Risk Management
- Performance Reports

---

# Milestone 6 – Dashboard

### Objectives

- Streamlit Dashboard
- Portfolio Overview
- Open Positions
- Closed Trades
- Equity Curve
- Performance Metrics
- Trade History

---

# Milestone 7 – Live Trading

### Objectives

- IG Markets Broker
- Live Orders
- Live Positions
- Account Synchronisation
- Risk Controls
- Real-Time Monitoring

---

# Milestone 8 – Artificial Intelligence

### Objectives

- AI Strategy Assistant
- Market Analysis
- Trade Suggestions
- Strategy Optimisation
- Portfolio Insights

---

# Guiding Principles

TradePilotAI is being developed with the following principles:

- Clean Architecture
- SOLID Design Principles
- Test-Driven Development
- Dependency Injection
- High Test Coverage
- Small, Incremental Changes
- Professional Documentation

---

# Current Priority

🎯 Complete the Trade Lifecycle.

Once Milestone 2 is complete, all future development will build on a fully functioning trading engine.