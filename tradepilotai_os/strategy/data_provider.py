"""Data provider for the Strategy Centre workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .service import StrategyService


class StrategyDataProvider:
    """Resolve strategy-centre data from the dependency container."""

    def __init__(self, container: Container | None = None, service: StrategyService | None = None) -> None:
        self.container = container
        self.service = service

    def get_strategy_data(self) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            service = self.container.resolve(StrategyService)
        if service is None:
            service = StrategyService()

        strategies = service.list_strategies()
        if not strategies:
            return {"strategies": [], "current_strategy": None, "events": []}

        strategy = strategies[0]
        return {
            "strategies": [self._serialize_strategy(item) for item in strategies],
            "current_strategy": self._serialize_strategy(strategy),
            "events": ["StrategyCreated", "StrategyUpdated", "StrategyVersionCreated", "StrategyDeployed", "StrategyArchived"],
        }

    def _serialize_strategy(self, strategy: Any) -> dict[str, Any]:
        return {
            "name": strategy.name,
            "version": strategy.version,
            "description": strategy.description,
            "status": strategy.status,
            "markets": strategy.markets,
            "timeframe": strategy.timeframe,
            "created_date": strategy.created_date,
            "last_modified": strategy.last_modified,
            "configuration": self._serialize_configuration(strategy.configuration),
            "performance": self._serialize_performance(strategy.performance),
            "versions": [self._serialize_version(version) for version in strategy.versions],
            "deployment": self._serialize_deployment(strategy.deployment),
        }

    def _serialize_configuration(self, config: Any) -> dict[str, Any]:
        return {
            "rsi_period": config.rsi_period,
            "rsi_buy_level": config.rsi_buy_level,
            "rsi_sell_level": config.rsi_sell_level,
            "ema_fast": config.ema_fast,
            "ema_slow": config.ema_slow,
            "risk_per_trade": config.risk_per_trade,
            "max_positions": config.max_positions,
            "reward_risk": config.reward_risk,
            "stop_loss": config.stop_loss,
            "take_profit": config.take_profit,
            "execution_mode": config.execution_mode,
        }

    def _serialize_performance(self, performance: Any) -> dict[str, Any]:
        return {
            "backtest_return": performance.backtest_return,
            "paper_return": performance.paper_return,
            "live_return": performance.live_return,
            "win_rate": performance.win_rate,
            "profit_factor": performance.profit_factor,
            "sharpe_ratio": performance.sharpe_ratio,
            "max_drawdown": performance.max_drawdown,
            "total_trades": performance.total_trades,
        }

    def _serialize_version(self, version: Any) -> dict[str, Any]:
        return {
            "version": version.version,
            "date": version.date,
            "author": version.author,
            "notes": version.notes,
        }

    def _serialize_deployment(self, deployment: Any) -> dict[str, Any] | None:
        if deployment is None:
            return None
        return {
            "target": deployment.target,
            "status": deployment.status,
            "broker_interface": deployment.broker_interface,
            "orchestrator": deployment.orchestrator,
        }
