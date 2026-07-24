# Changelog

All notable changes to TradePilotAI will be documented in this file.

This project follows the principles of incremental development, where each sprint delivers a tested, working improvement.

---

# [0.1.0] - In Development

## Milestone 1 - Core Trading Engine

### Added

- TradeSignal model
- TradeOrder model
- Position model
- Trade model
- PortfolioManager
- SimulationAccount
- Broker abstraction
- PaperBroker
- TradeEngine
- Unit test framework using pytest
- Dependency injection architecture

### Changed

- Refactored broker execution into a stable public interface.
- Improved separation of responsibilities between TradeEngine and Broker.
- Introduced private execution methods for BUY orders.

### Fixed

- Broker interface consistency.
- TradeEngine orchestration.
- Position management during BUY execution.

---

# [0.2.0] - Planned

## Milestone 2 - Complete Trade Lifecycle

### Planned

- SELL execution
- Trade history
- Integration tests
- Portfolio updates after SELL
- Cash settlement
- Completed trade workflow

---

# [0.3.0] - Planned

## Portfolio Analytics

### Planned

- Win rate
- Profit factor
- Equity curve
- Drawdown
- Performance reporting

---

# [0.4.0] - Planned

## Strategy Framework

### Planned

- Strategy interface
- Strategy registry
- Parameter optimisation
- Multiple trading strategies

---

# [0.5.0] - Planned

## Backtesting Engine

### Planned

- Historical data loader
- Backtest engine
- Commission modelling
- Slippage simulation
- Risk management
- Performance reports

---

# [0.6.0] - Planned

## Dashboard

### Planned

- Streamlit dashboard
- Portfolio overview
- Trade history
- Performance charts
- Analytics dashboard

---

# [1.0.0] - Future Release

## Live Trading Platform

### Planned

- IG Markets integration
- Live execution
- Live portfolio synchronisation
- Real-time monitoring
- Production-ready trading engine