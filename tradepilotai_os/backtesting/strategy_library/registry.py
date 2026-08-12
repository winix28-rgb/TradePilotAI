"""Strategy registry for discovering and instantiating backtest strategies."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable

from .interface import BacktestStrategy
from .models import StrategyParameter
from .strategies import EMATrendFollowingBacktestStrategy
from .strategies import MACDMomentumBacktestStrategy
from .strategies import RSIMeanReversionBacktestStrategy


@dataclass(frozen=True, slots=True)
class StrategyDefinition:
    strategy_id: str
    name: str
    description: str
    indicators: list[str]
    parameters: list[StrategyParameter]
    asset_class: str = ""
    primary_timeframe: str = ""
    supported_timeframes: list[str] = field(default_factory=list)
    category: str = ""
    version: str = ""
    author: str = ""
    supported_assets: list[str] | None = None
    supported_timeframes: list[str] | None = None
    supports_long: bool = True
    supports_short: bool = True
    risk_profile: str = ""
    best_market: str = ""
    best_timeframes: list[str] | None = None
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    recommended_risk: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "asset_class": self.asset_class,
            "primary_timeframe": self.primary_timeframe,
            "supported_timeframes": list(self.supported_timeframes),
            "description": self.description,
            "indicators": list(self.indicators),
            "parameters": [item.to_dict() for item in self.parameters],
            "category": self.category,
            "version": self.version,
            "author": self.author,
            "supported_assets": list(self.supported_assets or []),
            "supports_long": self.supports_long,
            "supports_short": self.supports_short,
            "risk_profile": self.risk_profile,
            "best_market": self.best_market,
            "best_timeframes": list(self.best_timeframes or []),
            "strengths": list(self.strengths or []),
            "weaknesses": list(self.weaknesses or []),
            "recommended_risk": self.recommended_risk,
        }


class StrategyRegistry:
    """Simple in-memory registry for built-in strategy classes."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[dict[str, Any] | None], BacktestStrategy]] = {
            "rsi_mean_reversion": lambda params=None: RSIMeanReversionBacktestStrategy(params),
            "ema_trend_following": lambda params=None: EMATrendFollowingBacktestStrategy(params),
            "macd_momentum": lambda params=None: MACDMomentumBacktestStrategy(params),
        }

    def list_definitions(self) -> list[StrategyDefinition]:
        definitions: list[StrategyDefinition] = []
        for strategy_id, factory in self._factories.items():
            instance = factory(None)
            definitions.append(
                StrategyDefinition(
                    strategy_id=strategy_id,
                    name=instance.name,
                    asset_class=str(getattr(instance, "asset_class", "")),
                    primary_timeframe=str(getattr(instance, "primary_timeframe", "")),
                    supported_timeframes=list(getattr(instance, "supported_timeframes", []) or []),
                    description=instance.description,
                    indicators=list(instance.indicators),
                    parameters=list(instance.parameters),
                    category=str(getattr(instance, "category", "")),
                    version=str(getattr(instance, "version", "")),
                    author=str(getattr(instance, "author", "")),
                    supported_assets=list(getattr(instance, "supported_assets", []) or []),
                    supports_long=bool(getattr(instance, "supports_long", True)),
                    supports_short=bool(getattr(instance, "supports_short", True)),
                    risk_profile=str(getattr(instance, "risk_profile", "")),
                    best_market=str(getattr(instance, "best_market", "")),
                    best_timeframes=list(getattr(instance, "best_timeframes", []) or []),
                    strengths=list(getattr(instance, "strengths", []) or []),
                    weaknesses=list(getattr(instance, "weaknesses", []) or []),
                    recommended_risk=str(getattr(instance, "recommended_risk", "")),
                )
            )
        return definitions

    def get_definition(self, strategy_id: str) -> StrategyDefinition | None:
        factory = self._factories.get(strategy_id)
        if factory is None:
            return None
        instance = factory(None)
        return StrategyDefinition(
            strategy_id=strategy_id,
            name=instance.name,
            asset_class=str(getattr(instance, "asset_class", "")),
            primary_timeframe=str(getattr(instance, "primary_timeframe", "")),
            supported_timeframes=list(getattr(instance, "supported_timeframes", []) or []),
            description=instance.description,
            indicators=list(instance.indicators),
            parameters=list(instance.parameters),
            category=str(getattr(instance, "category", "")),
            version=str(getattr(instance, "version", "")),
            author=str(getattr(instance, "author", "")),
            supported_assets=list(getattr(instance, "supported_assets", []) or []),
            supports_long=bool(getattr(instance, "supports_long", True)),
            supports_short=bool(getattr(instance, "supports_short", True)),
            risk_profile=str(getattr(instance, "risk_profile", "")),
            best_market=str(getattr(instance, "best_market", "")),
            best_timeframes=list(getattr(instance, "best_timeframes", []) or []),
            strengths=list(getattr(instance, "strengths", []) or []),
            weaknesses=list(getattr(instance, "weaknesses", []) or []),
            recommended_risk=str(getattr(instance, "recommended_risk", "")),
        )

    def create(self, strategy_id: str, parameters: dict[str, Any] | None = None) -> BacktestStrategy:
        factory = self._factories.get(strategy_id)
        if factory is None:
            available = ", ".join(sorted(self._factories.keys()))
            raise ValueError(f"Unknown strategy '{strategy_id}'. Available: {available}")
        return factory(parameters)

    @property
    def default_strategy_id(self) -> str:
        return "rsi_mean_reversion"
