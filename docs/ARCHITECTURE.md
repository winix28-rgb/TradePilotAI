# TradePilotAI Architecture

**Version:** 1.0
**Status:** Active Design Document

---

# Vision

TradePilotAI is a modular algorithmic trading platform designed to support:

- Historical backtesting
- Paper trading
- Live trading
- Multiple trading strategies
- Multiple brokers
- Portfolio management
- Professional reporting

The same strategy code should run unchanged in all environments.

---

# Core Design Principles

## Single Responsibility Principle

Every class has one responsibility.

Examples:

- DataLoader loads market data.
- IndicatorEngine calculates indicators.
- StrategyEngine runs strategies.
- TradeRecorder records completed trades.

---

## Separation of Concerns

Market Data
↓

Indicators
↓

Strategy
↓

Signals
↓

Trade Recording
↓

Portfolio
↓

Reporting

Each layer communicates only with the next layer.

---

## Strategy Independence

Strategies generate trading signals only.

They do NOT:

- Execute trades
- Calculate profits
- Generate reports
- Manage portfolios

---

# Project Structure

TradePilotAI/

config/
core/
data/
indicators/
strategies/
signals/
models/
backtesting/
reports/
portfolio/
brokers/
tests/
docs/

---

# Long-Term Goal

TradePilotAI should evolve into a professional trading platform capable of:

- Portfolio optimisation
- Walk-forward testing
- Monte Carlo analysis
- Risk management
- Multi-broker execution
- AI-assisted strategy development
