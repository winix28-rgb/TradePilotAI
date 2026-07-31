# Risk Dashboard Module

## Architecture

The Risk Dashboard module follows the same composition pattern as the other TradePilotAI OS workspaces:

- Page: renders the risk workspace and coordinates the summary, exposure, rules, and timeline sections.
- Components: shared cards and tables for KPI values, exposure, positions, rules, and timeline events.
- Service: owns the risk snapshot and event subscriptions.
- Data Provider: resolves data from the dependency container.
- Models: typed domain objects for assessments, exposures, positions, rules, violations, and snapshots.
- Events: lightweight lifecycle events for risk updates and breaches.

## Models

- RiskAssessment: overall portfolio and position risk metrics.
- PortfolioExposure: exposure grouped by category.
- PositionRisk: per-symbol risk metrics.
- RiskRule: configured rule values with status.
- RiskViolation: warning or breach conditions.
- RiskSnapshot: aggregate snapshot for rendering.

## Services

- RiskDashboardService builds a sample risk snapshot and exposes refresh and event-subscription hooks.

## Events

The module publishes and consumes:

- RiskUpdated
- RiskViolationDetected
- ExposureChanged
- RiskRuleBreached

## Future extensions

- Connect this workspace to a live portfolio or broker service.
- Replace the placeholder snapshot with persisted policy state.
- Add drill-down views for each risk rule or position.
