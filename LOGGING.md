# TradePilotAI OS Logging

## Architecture

TradePilotAI OS uses a centralized structured logging layer built around a shared logger API and a correlation context.

### Components

- Structured logger: emits JSON payloads with timestamp, level, module, message, correlation ID, thread, and context.
- Configuration entry point: configures console and file handlers, including rotating file output.
- Infrastructure service: wires the configured logger into the application lifecycle.
- Exception handler: sends operational failures through the shared logger so issues are visible in one place.

### Workflow tracing

A trading workflow shares one correlation ID from scanner to signal to risk to broker to portfolio to history and dashboard. The shared context manager ensures that every stage contributes to the same workflow trace.

## Configuration

The logger is configured through the application configuration under the logging section.

Example:

```json
{
  "logging": {
    "level": "INFO",
    "console_enabled": true,
    "file_enabled": true,
    "file_path": "logs/tradepilotai.log",
    "max_bytes": 5242880,
    "backup_count": 3
  }
}
```

Supported levels:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

## Usage

```python
from tradepilotai_os.operations import create_logger
from tradepilotai_os.operations.logging_service import correlation_context

logger = create_logger("TradePilotAI")
logger.info("startup", module="application")

with correlation_context("workflow-123"):
    logger.info("scanner event", module="scanner")
```

## Correlation IDs

Every workflow should share a single correlation ID. The context manager ensures that nested operations inherit and emit the same ID.

## Rotation

The default file handler uses rotating file output so logs do not grow indefinitely. The rotation size and backup count are configurable.
