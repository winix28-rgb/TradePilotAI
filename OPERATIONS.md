# TradePilotAI OS Operations

## Logging

Structured logging is centralized through the operations package. Each log entry includes a timestamp, level, module, message, optional correlation ID, and context payload. The logger captures workflow context for scanner, risk, portfolio, orders, broker, strategy, backtesting, and application modules.

## Health checks

The HealthCheckService aggregates readiness for the broker interface, portfolio, scanner, risk engine, strategy engine, notifications, refresh manager, event bus, orchestrator, and dependency container.

## Startup validation

Startup validation checks configuration presence, required dependency registrations, and required navigation routes before the platform begins serving pages.

## Failure handling

Centralized exception handling captures unhandled exceptions and emits user-friendly operational warnings.
