# Live Trading Module

## Architecture

The Live Trading module is a broker-facing workspace that stays decoupled from portfolio, risk, and scanner logic. It depends on the shared broker abstraction and presents order workflow state through a page/service/data-provider pattern.

## Workflow

1. The ticket form collects an order request.
2. The service validates the request against pre-trade checks.
3. The service publishes lifecycle events for creation, validation, submission, acceptance, fill, partial fill, cancel, rejection, and close.
4. The broker interface executes the order without leaking broker-specific implementation details into the workspace.

## Broker integration

The workspace communicates exclusively through the Broker interface in [tradepilotai_os/broker/base.py](tradepilotai_os/broker/base.py).

## Order lifecycle

The workspace surfaces the lifecycle flow through its UI:

Created -> Validated -> Submitted -> Accepted -> Partially Filled -> Filled -> Closed

## Future extensions

- Add real order cancellation and amendment flows.
- Connect the workspace to a live broker adapter.
- Render richer execution analytics and blotters.
