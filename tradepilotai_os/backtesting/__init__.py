"""Backtesting components for the TradePilotAI OS."""

from .backtest_engine import BacktestEngine
from .comparison import StrategyComparisonEngine
from .comparison import StrategyComparisonResult
from .components import BacktestChartCard, BacktestKpiCard, BacktestStatsTable, BacktestSummarySection, BacktestTradeList
from .data_provider import BacktestingDataProvider
from .performance_engine import PerformanceEngine
from .portfolio_simulator import PortfolioSimulator
from .result import BacktestResult
from .result import BacktestTradeRecord
from .sample_backtest_result import GoldenResearchDataset
from .sample_backtest_result import create_golden_backtest_result
from .sample_backtest_result import create_golden_research_dataset
from .strategy_library import StrategyDefinition
from .strategy_library import StrategyRegistry
from .page import BacktestingPage
from .service import BacktestingService
from .trade_simulator import TradeSimulator

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "BacktestTradeRecord",
    "StrategyComparisonEngine",
    "StrategyComparisonResult",
    "GoldenResearchDataset",
    "create_golden_backtest_result",
    "create_golden_research_dataset",
    "StrategyDefinition",
    "StrategyRegistry",
    "TradeSimulator",
    "PortfolioSimulator",
    "PerformanceEngine",
    "BacktestingPage",
    "BacktestingDataProvider",
    "BacktestingService",
    "BacktestChartCard",
    "BacktestKpiCard",
    "BacktestStatsTable",
    "BacktestSummarySection",
    "BacktestTradeList",
]
