"""
===========================================================
TradePilotAI
Application Configuration
===========================================================

Root configuration object for the entire application.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from models.backtest_config import BacktestConfig
from models.market_config import MarketConfig
from models.risk_config import RiskConfig
from models.strategy_config import StrategyConfig


@dataclass(slots=True, frozen=True)
class ApplicationConfig:
    """
    Root configuration object.

    Groups together every configuration section
    used by the application.
    """

    strategy: StrategyConfig = field(default_factory=StrategyConfig)

    risk: RiskConfig = field(default_factory=RiskConfig)

    backtest: BacktestConfig = field(default_factory=BacktestConfig)

    market: MarketConfig = field(default_factory=MarketConfig)