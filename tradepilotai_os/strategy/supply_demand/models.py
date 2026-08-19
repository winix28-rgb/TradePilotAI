"""
===========================================================
TradePilotAI OS
Supply & Demand Strategy Models
===========================================================

Data models used by the Supply & Demand strategy.

This module contains data structures only.
Trading logic belongs in the strategy components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class TrendDirection(str, Enum):
    """Directional classification used by the strategy."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class MarketStructure(str, Enum):
    """H1 market-structure classification."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    CONSOLIDATION = "CONSOLIDATION"
    UNKNOWN = "UNKNOWN"


class SwingType(str, Enum):
    """Individual H1 swing classifications."""

    HIGHER_HIGH = "HH"
    HIGHER_LOW = "HL"
    LOWER_HIGH = "LH"
    LOWER_LOW = "LL"


class ZoneType(str, Enum):
    """Supply or Demand zone."""

    DEMAND = "DEMAND"
    SUPPLY = "SUPPLY"


class ZoneStatus(str, Enum):
    """Lifecycle state of a Supply/Demand zone."""

    ACTIVE = "ACTIVE"
    RETESTING = "RETESTING"
    MITIGATED = "MITIGATED"
    TRADED = "TRADED"


class EntryPattern(str, Enum):
    """Valid S&D entry patterns."""

    PIN_BAR = "PIN_BAR"
    ENGULFING = "ENGULFING"
    THREE_CANDLE_REVERSAL = "THREE_CANDLE_REVERSAL"


class TrendAlignment(str, Enum):
    """Relationship between the trade and the established trend."""

    WITH_TREND = "WITH_TREND"
    AGAINST_TREND = "AGAINST_TREND"
    UNCLEAR = "UNCLEAR"


@dataclass(slots=True)
class TimeframeTrend:
    """
    Trend assessment for Daily or H4.

    The strategy uses the 50-period and 200-period moving averages
    together with candle direction relative to those averages.
    """

    timeframe: str
    direction: TrendDirection = TrendDirection.NEUTRAL

    ma50: Optional[float] = None
    ma200: Optional[float] = None

    price: Optional[float] = None

    candles_with_trend: bool = False

    explanation: str = ""


@dataclass(slots=True)
class SwingPoint:
    """An identified H1 swing point."""

    timestamp: Any
    price: float
    swing_type: SwingType

    index: Optional[int] = None


@dataclass(slots=True)
class H1Structure:
    """Current H1 market structure."""

    direction: MarketStructure = MarketStructure.UNKNOWN

    latest_swing: Optional[SwingPoint] = None

    swing_points: list[SwingPoint] = field(default_factory=list)

    higher_highs: list[SwingPoint] = field(default_factory=list)
    higher_lows: list[SwingPoint] = field(default_factory=list)

    lower_highs: list[SwingPoint] = field(default_factory=list)
    lower_lows: list[SwingPoint] = field(default_factory=list)

    explanation: str = ""


@dataclass(slots=True)
class SupplyDemandZone:
    """
    Represents one Supply or Demand zone.

    The lifecycle explicitly records the different candles involved
    in the strategy:

        structure-start candle
                ↓
        breakout candle
                ↓
        entry candle
                ↓
        trade-start candle
                ↓
        trade

    The entry candle is the candle that confirms the entry pattern.

    The trade starts at the OPEN of the candle immediately following
    the entry candle.
    """

    symbol: str
    zone_type: ZoneType

    top: float
    bottom: float

    created_at: Any
    breakout_time: Any

    status: ZoneStatus = ZoneStatus.ACTIVE

    # ---------------------------------------------------------
    # Structure / breakout
    # ---------------------------------------------------------

    structure_start_time: Optional[Any] = None
    structure_start_price: Optional[float] = None

    breakout_price: Optional[float] = None

    # ---------------------------------------------------------
    # Retest
    # ---------------------------------------------------------

    retest_started_at: Optional[Any] = None
    retest_candle_count: int = 0

    # ---------------------------------------------------------
    # Entry candle
    # ---------------------------------------------------------

    entry_pattern: Optional[EntryPattern] = None
    entry_candle_time: Optional[Any] = None
    entry_candle_close: Optional[float] = None

    # ---------------------------------------------------------
    # Trade-start candle
    # ---------------------------------------------------------

    trade_start_time: Optional[Any] = None
    trade_start_price: Optional[float] = None

    # ---------------------------------------------------------
    # Actual trade levels
    # ---------------------------------------------------------

    entry_time: Optional[Any] = None
    entry_price: Optional[float] = None

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    # ---------------------------------------------------------
    # Zone lifecycle
    # ---------------------------------------------------------

    mitigation_time: Optional[Any] = None
    mitigation_reason: Optional[str] = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def height(self) -> float:
        """Return the price height of the zone."""

        return abs(self.top - self.bottom)

    @property
    def is_active(self) -> bool:
        """Return True while the zone can still produce an entry."""

        return self.status in {
            ZoneStatus.ACTIVE,
            ZoneStatus.RETESTING,
        }

    def contains_price(self, price: float) -> bool:
        """Return True when price is inside the zone."""

        return self.bottom <= float(price) <= self.top


@dataclass(slots=True)
class SupplyDemandContext:
    """
    Complete market context used when evaluating an S&D setup.
    """

    symbol: str

    daily_trend: TimeframeTrend
    h4_trend: TimeframeTrend
    h1_structure: H1Structure

    trend_alignment: TrendAlignment = TrendAlignment.UNCLEAR

    active_zones: list[SupplyDemandZone] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SupplyDemandTradeContext:
    """
    Strategy information captured when an S&D trade is generated.

    This information will later feed the trade journal.
    """

    symbol: str

    zone_type: ZoneType
    entry_pattern: EntryPattern

    daily_trend: TrendDirection
    h4_trend: TrendDirection
    h1_structure: MarketStructure

    trend_alignment: TrendAlignment

    structure_start_time: Optional[Any]
    breakout_time: Optional[Any]
    entry_candle_time: Optional[Any]
    trade_start_time: Optional[Any]

    zone_top: float
    zone_bottom: float

    entry_price: float
    stop_loss: float
    take_profit: float

    risk_percent: float = 0.01
    risk_value: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)