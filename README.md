# TradePilotAI

> A professional algorithmic trading platform written in Python.

---

## Overview

TradePilotAI is a modular algorithmic trading framework designed to support:

- Paper Trading
- Strategy Development
- Portfolio Management
- Backtesting
- Performance Analytics
- Live Trading (IG Markets)

The project has been built using clean architecture principles so that every component has a single responsibility and can be independently tested.

The long-term objective is to create a professional-grade trading platform capable of researching, testing and executing systematic trading strategies.

---

# Current Features

## Trading Models

- TradeSignal
- TradeOrder
- Position
- Trade

## Portfolio

- PortfolioManager
- SimulationAccount

## Execution

- Broker Interface
- PaperBroker
- TradeEngine

## Risk Management

- Stop Loss
- Take Profit

## Testing

- pytest
- Unit Tests
- Integration Tests (In Progress)

---

# Architecture

```
                Strategy
                     │
                     ▼
              TradeSignal
                     │
                     ▼
              TradeOrder
                     │
                     ▼
              TradeEngine
                     │
                     ▼
          Broker.execute(order)
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
  PaperBroker              Future IGBroker
        │
        ▼
PortfolioManager
        │
        ▼
SimulationAccount
```

---

# Design Principles

TradePilotAI follows several software engineering principles.

## Single Responsibility Principle

Each class has one job.

Examples:

- Trade represents a completed trade.
- Position represents an open trade.
- TradeEngine coordinates execution.
- PaperBroker executes orders.
- PortfolioManager manages positions.

---

## Dependency Injection

TradeEngine depends on the Broker interface rather than a specific broker implementation.

This allows PaperBroker to be replaced with an IGBroker without changing the rest of the application.

---

## Test Driven Development

Every feature is developed alongside automated tests.

The goal is to maintain a green test suite throughout development.

---

# Project Structure

```
TradePilotAI/

├── brokers/
├── core/
├── indicators/
├── models/
├── portfolio/
├── services/
├── signals/
├── strategies/
├── tests/

├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

---

# Installation

Clone the repository.

```bash
git clone https://github.com/<your-username>/TradePilotAI.git
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Running Tests

```bash
python -m pytest -v
```

---

# Current Status

Current Version

```
v0.1.0 (Development)
```

Current Milestone

```
Milestone 2
Complete Trade Lifecycle
```

---

# Roadmap

- Complete SELL execution
- Trade History
- Portfolio Analytics
- Backtesting Engine
- Performance Dashboard
- Live IG Markets Integration
- Machine Learning Strategy Optimisation

---

# Author

Developed by Wilhelm.

Built with Python, pytest and a passion for systematic trading.

---

# License

This project is licensed under the MIT License.