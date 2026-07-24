"""
===========================================================
TradePilotAI
Constants
Version 3.0
===========================================================

Application-wide constant values.
"""

from enum import Enum


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class ExitReason(str, Enum):
    RSI_TARGET = "RSI Target"
    STOP_LOSS = "Stop Loss"
    MANUAL = "Manual"
    TIMEOUT = "Setup Timeout"