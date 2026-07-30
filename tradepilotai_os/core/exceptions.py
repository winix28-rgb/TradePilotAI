"""
============================================================
TradePilotAI Operating System
Exception Framework
============================================================
"""


class TradePilotError(Exception):
    """Base exception for the application."""


class ConfigurationError(TradePilotError):
    """Raised when configuration is invalid."""


class ServiceError(TradePilotError):
    """Raised when a service fails."""


class ServiceNotFoundError(ServiceError):
    """Raised when a requested service is not registered."""


class DuplicateServiceError(ServiceError):
    """Raised when attempting to register a duplicate service."""


class StartupError(TradePilotError):
    """Raised when application startup fails."""


class ShutdownError(TradePilotError):
    """Raised when application shutdown fails."""


class ValidationError(TradePilotError):
    """Raised when validation fails."""
