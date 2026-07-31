# Trade History Module

## Architecture

The Trade History module follows the same composition pattern as the dashboard, portfolio, and scanner workspaces:

- Page: renders the workspace shell and coordinates visual sections.
- Components: reusable cards, tables, and detail panels.
- Service: owns trade state, lifecycle updates, and derived summary metrics.
- Data Provider: resolves live or fallback data from the DI container.
- Models: typed domain objects for trades, summaries, statistics, and timelines.
- Events: lightweight lifecycle events for trade-open, update, close, and cancel actions.

## Services

- TradeHistoryService provides typed trade records and summary calculations.
- TradeHistoryDataProvider resolves data for the page using the application container.

## Models

- Trade: the core trade record with execution, risk, and lifecycle information.
- TradeSummary: KPI-style summary values for the journal dashboard.
- TradeStatistics: supporting analytics values.
- TradeTimeline: a simple timeline of trade-state changes.

## Events

The module supports these lifecycle events:

- TradeOpened
- TradeUpdated
- TradeClosed
- TradeCancelled

## Extension points

- Replace the placeholder service with a persistent repository.
- Connect the page to a live broker or portfolio integration.
- Add richer filtering and search capabilities.
