# Contributing to TradePilotAI

Thank you for your interest in contributing to TradePilotAI.

The goal of this project is to build a professional-quality algorithmic trading platform using modern software engineering principles.

Whether you are fixing a bug, improving documentation or adding a new feature, please follow the guidelines below.

---

# Development Philosophy

TradePilotAI is built around five core principles:

- Clean Architecture
- SOLID Design Principles
- Test-Driven Development
- Incremental Development
- Readable, Maintainable Code

Every contribution should improve the project without reducing its quality.

---

# Development Workflow

Each feature follows the same workflow.

1. Design the change.
2. Make one small change.
3. Run all tests.
4. Ensure all tests pass.
5. Commit the change.
6. Push to GitHub.

Avoid making multiple unrelated changes in the same commit.

---

# Coding Standards

## General

- Keep functions short and focused.
- Keep classes responsible for one task.
- Use descriptive names.
- Write docstrings for public classes and methods.
- Follow PEP 8 style guidelines.

---

## Architecture

TradePilotAI follows a layered architecture.

```
Strategy
    ↓
TradeSignal
    ↓
TradeOrder
    ↓
TradeEngine
    ↓
Broker
    ↓
PortfolioManager
    ↓
SimulationAccount
```

Each layer has a single responsibility.

Do not allow business logic to leak into unrelated components.

---

# Testing

Every new feature should include appropriate tests.

Before committing, always run:

```bash
python -m pytest -v
```

The test suite must pass before changes are committed.

---

# Commit Messages

Use clear, descriptive commit messages.

Examples:

```
feat: add SELL execution to PaperBroker
```

```
test: add PaperBroker SELL tests
```

```
refactor: simplify TradeEngine workflow
```

```
docs: update project roadmap
```

```
fix: correct trade profit calculation
```

---

# Pull Requests

If contributing through pull requests:

- Keep changes focused.
- Explain why the change is needed.
- Reference related issues if applicable.
- Ensure all tests pass before requesting review.

---

# Documentation

Whenever a feature is added, update the relevant documentation:

- README.md
- ROADMAP.md
- CHANGELOG.md

Documentation should evolve alongside the code.

---

# Code Reviews

When reviewing code, consider:

- Correctness
- Readability
- Maintainability
- Test Coverage
- Architecture
- Performance (where relevant)

Constructive feedback is encouraged.

---

# Long-Term Vision

TradePilotAI aims to become a complete algorithmic trading platform supporting:

- Strategy Development
- Backtesting
- Portfolio Analytics
- Paper Trading
- Live Trading
- AI-Assisted Research

Every contribution should move the project closer to this goal.

---

# Thank You

Thank you for helping improve TradePilotAI.

Build carefully.
Test thoroughly.
Keep learning.