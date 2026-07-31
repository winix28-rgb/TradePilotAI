# TradePilotAI OS System Architecture

## Platform goals

The TradePilotAI OS platform is organized as a set of cohesive workspaces that share common shell, navigation, refresh, event, and broker abstractions. The architecture favors modularity, dependency injection, and explicit service boundaries over direct cross-module coordination.

## Core layers

- Workspace layer: dashboard, portfolio, scanner, backtesting, trade history, risk, live trading, and strategy centre pages.
- Service layer: page data providers, orchestration services, and domain services.
- Domain layer: shared models for orders, trades, strategies, portfolio, risk, signals, and broker execution.
- Infrastructure layer: container, logging, notifications, refresh management, and event bus.

## Integration principles

- Pages inherit from a shared workspace base class.
- Navigation routes are resolved through NavigationService.
- The ApplicationOrchestrator sequences scanner, risk, broker, portfolio, trade history, refresh, and notifications.
- The broker abstraction is unified through BrokerInterface.
- Event propagation uses an in-memory event bus that modules can subscribe to.
