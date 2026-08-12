"""Backtest result model for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from tradepilotai_os.models.portfolio import Portfolio
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.models.trade_signal import TradeSignal


@dataclass(slots=True)
class BacktestTradeRecord:
    """Completed trade record with execution costs and lifecycle details."""

    symbol: str
    direction: str
    entry_date: Any
    entry_price: float
    exit_date: Any
    exit_price: float
    quantity: int
    gross_pnl: float
    costs: float
    net_pnl: float
    exit_reason: str
    stop_loss: float | None = None
    take_profit: float | None = None
    commission: float = 0.0
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    reference_entry_price: float | None = None
    reference_exit_price: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BacktestResult:
    """Structured result returned by the backtest engine."""

    initial_cash: float = 0.0
    requested_symbols: list[str] = field(default_factory=list)
    loaded_symbols: list[str] = field(default_factory=list)
    failed_symbols: dict[str, str] = field(default_factory=dict)
    completion_status: str = "pending"
    trades: list[BacktestTradeRecord] = field(default_factory=list)
    closed_trades: list[BacktestTradeRecord] = field(default_factory=list)
    open_trades: list[Trade] = field(default_factory=list)
    portfolio: Portfolio = field(default_factory=Portfolio)
    metrics: dict[str, Any] = field(default_factory=dict)
    equity_curve: list[tuple[Any, float]] = field(default_factory=list)
    running_equity: list[tuple[Any, float]] = field(default_factory=list)
    peak_equity: list[tuple[Any, float]] = field(default_factory=list)
    drawdown_series: list[tuple[Any, float]] = field(default_factory=list)
    drawdown_curve: list[tuple[Any, float]] = field(default_factory=list)
    signals: list[TradeSignal] = field(default_factory=list)
    symbol_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a compatibility dictionary for existing dashboard consumers."""

        return {
            "summary": self._summary(),
            "requested_symbols": list(self.requested_symbols),
            "loaded_symbols": list(self.loaded_symbols),
            "failed_symbols": dict(self.failed_symbols),
            "completion_status": self.completion_status,
            "metrics": self.metrics,
            "portfolio": self._portfolio_dict(),
            "results": [trade.as_dict() for trade in self.closed_trades],
            "executed_trades": len(self.closed_trades),
            "trades": [trade.as_dict() for trade in self.trades],
            "closed_trades": [trade.as_dict() for trade in self.closed_trades],
            "open_trades": [asdict(trade) for trade in self.open_trades],
            "equity_curve": list(self.equity_curve),
            "running_equity": list(self.running_equity),
            "peak_equity": list(self.peak_equity),
            "drawdown_series": list(self.drawdown_series),
            "drawdown_curve": list(self.drawdown_curve),
            "signals": [asdict(signal) for signal in self.signals],
            "symbol_results": self.symbol_results,
        }

    def _summary(self) -> dict[str, Any]:
        return {
            "status": self.completion_status if self.completion_status != "pending" else ("completed" if self.closed_trades or self.symbol_results else "pending"),
            "source": "backtest_engine",
            "initial_cash": self.initial_cash,
            "closed_trades": len(self.closed_trades),
        }

    def _portfolio_dict(self) -> dict[str, Any]:
        return {
            "cash": self.portfolio.cash,
            "realised_pnl": self.portfolio.realised_pnl,
            "unrealised_pnl": self.portfolio.unrealised_pnl,
            "exposure": self.portfolio.exposure,
            "positions": {
                symbol: asdict(position)
                for symbol, position in self.portfolio.positions.items()
            },
            "metadata": dict(self.portfolio.metadata),
        }