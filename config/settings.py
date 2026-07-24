"""
===========================================================
TradePilotAI
Configuration Settings
Version 3.0
===========================================================

All application settings are stored here.

Changing a value here automatically changes the behaviour
of the trading system.
"""

# ==========================================================
# ACCOUNT SETTINGS
# ==========================================================

ACCOUNT_SIZE = 100000

RISK_PER_TRADE = 0.01          # 1%

MAX_OPEN_POSITIONS = 10

COMMISSION = 0.0

SLIPPAGE = 0.0


# ==========================================================
# INDICATORS
# ==========================================================

EMA_FAST = 12

EMA_SLOW = 26

RSI_PERIOD = 14


# ==========================================================
# STRATEGY
# ==========================================================

BUY_RSI = 30

SELL_RSI = 70

EXIT_RSI = 50

SETUP_TIMEOUT = 10


# ==========================================================
# BACKTEST
# ==========================================================

START_DATE = "2015-01-01"

END_DATE = "2030-01-01"

DEFAULT_MARKET = "FTSE100"


# ==========================================================
# REPORTING
# ==========================================================

SHOW_DEBUG = True

SAVE_TRADE_LOG = True

SAVE_REPORT = True