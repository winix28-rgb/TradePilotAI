"""Trade History workspace package for the TradePilotAI OS."""

from .components import TradeDetailCard, TradeFiltersCard, TradeHistoryKpiCard, TradeHistoryTable
from .data_provider import TradeHistoryDataProvider
from .events import EventBus, TradeEvent
from .models import Trade, TradeStatistics, TradeSummary, TradeTimeline
from .page import TradeHistoryPage
from .service import TradeHistoryService

__all__ = [
    "Trade",
    "TradeDetailCard",
    "EventBus",
    "TradeEvent",
    "TradeFiltersCard",
    "TradeHistoryDataProvider",
    "TradeHistoryPage",
    "TradeHistoryService",
    "TradeHistoryKpiCard",
    "TradeHistoryTable",
    "TradeStatistics",
    "TradeSummary",
    "TradeTimeline",
]
