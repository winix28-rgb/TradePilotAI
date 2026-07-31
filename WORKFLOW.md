# TradePilotAI OS Workflow

## End-to-end workflow

1. The scanner identifies candidate opportunities.
2. Risk evaluates the proposed trade.
3. The broker executes the trade through the broker interface.
4. The portfolio updates based on execution results.
5. Trade history records the completed trade.
6. Dashboard refresh and notification services are triggered.

## Platform responsibilities

- Scanner: scans markets and produces watchlist signals.
- Risk: validates trade acceptability and sizing.
- Broker: executes order logic.
- Portfolio: updates positions and cash.
- Trade history: records completed activity.
- Dashboard refresh: updates the UI state.
- Notifications: surfaces workflow results.
