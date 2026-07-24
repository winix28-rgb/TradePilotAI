from pathlib import Path

# ------------------------------------------------------------
# TradePilotAI Documentation Creator
# ------------------------------------------------------------

docs = Path("docs")
docs.mkdir(exist_ok=True)

files = {
    "ARCHITECTURE.md": """# TradePilotAI Architecture

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
""",

    "ROADMAP.md": """# TradePilotAI Roadmap

## Sprint 1 ✅

- Project structure
- Git repository
- Data loading
- Indicator engine

---

## Sprint 2 ✅

- Strategy framework
- RSI Mean Reversion strategy
- Strategy engine
- Trade recorder

---

## Sprint 3 🚧

- Statistics engine
- Performance calculations
- Backtest report

---

## Sprint 4

- Portfolio management
- Position sizing
- Risk management

---

## Sprint 5

- Multi-stock backtesting

---

## Sprint 6

- Interactive dashboard

---

## Sprint 7

- Paper trading

---

## Sprint 8

- IG Markets integration

---

## Sprint 9

- Live trading

---

## Future

- AI strategy builder
- Walk-forward optimisation
- Monte Carlo simulation
""",

    "CHANGELOG.md": """# Changelog

## Sprint 1

- Initial project created
- Git repository configured
- DataLoader implemented
- IndicatorEngine implemented

---

## Sprint 2

- BaseStrategy created
- RSI Mean Reversion strategy implemented
- StrategyEngine implemented
- TradeRecorder implemented
- Trade history working

---

## Sprint 3

In Progress
""",

    "CODING_STANDARDS.md": """# Coding Standards

## General Principles

- One class, one responsibility.
- One function, one job.
- Prefer readability over cleverness.
- Use type hints.
- Write docstrings.

---

## Naming

Classes:
PascalCase

Functions:
snake_case

Variables:
snake_case

Constants:
UPPER_CASE

---

## Architecture

Strategies generate signals.

Backtesting executes trades.

Portfolio manages positions.

Reporting analyses results.

---

## Git Workflow

Every feature should be:

1. Tested
2. Committed
3. Documented

---

## Philosophy

Build software that is:

- Modular
- Testable
- Extensible
- Maintainable
"""
}

for filename, content in files.items():
    path = docs / filename
    path.write_text(content, encoding="utf-8")
    print(f"Created: {path}")

print("\n✅ Documentation created successfully!")