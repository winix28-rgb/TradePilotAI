# Strategy Centre Module

## Architecture

The Strategy Centre is a self-contained workspace that follows the TradePilotAI OS module pattern. The page owns presentation, the service owns lifecycle management and deployment coordination, the data provider resolves data from dependency injection, and the event bus propagates lifecycle notifications across the application.

## Versioning

Strategies are versioned as immutable snapshots. New versions can be created and appended without overwriting prior history. Each version records author, date, and notes for auditability.

## Deployment

Deployment uses the broker interface and application orchestrator abstraction. The strategy service can target either a paper broker or a live broker through the shared broker contract.

## Workflow

1. Create or update a strategy.
2. Configure indicators, risk, and execution settings.
3. Create a new version for audit and evaluation.
4. Deploy to paper or live through the broker interface.
5. Archive strategies once they are no longer active.

## Future extensions

- Add strategy backtesting and walk-forward analysis.
- Introduce role-based approvals before deployment.
- Create richer performance dashboards and alerts.
