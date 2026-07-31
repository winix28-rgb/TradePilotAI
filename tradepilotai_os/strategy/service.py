"""Service layer for the Strategy Centre workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.broker.base import Broker, ExecutionResult
from tradepilotai_os.models.trade import Trade

from .events import EventBus
from .models import Strategy, StrategyConfiguration, StrategyDeployment, StrategyPerformance, StrategyVersion


class StrategyService:
    """Manage strategy lifecycle, versioning, deployment, and refresh state."""

    def __init__(self, broker: Broker | None = None, event_bus: EventBus | None = None) -> None:
        self.broker = broker
        self.event_bus = event_bus or EventBus()
        self._refresh_count = 0
        self._events: list[str] = []
        self._strategies: list[Strategy] = []
        self._seed_default_strategy()

    def list_strategies(self) -> list[Strategy]:
        return list(self._strategies)

    def create_strategy(self, strategy: Strategy) -> Strategy:
        self._strategies.append(strategy)
        self._publish("StrategyCreated", {"strategy": strategy})
        return strategy

    def update_strategy(self, strategy: Strategy) -> Strategy:
        for index, existing in enumerate(self._strategies):
            if existing.name == strategy.name:
                self._strategies[index] = strategy
                self._publish("StrategyUpdated", {"strategy": strategy})
                return strategy
        return self.create_strategy(strategy)

    def create_version(self, strategy: Strategy, version: StrategyVersion) -> Strategy:
        strategy.versions.append(version)
        strategy.version = version.version
        strategy.last_modified = version.date
        self._publish("StrategyVersionCreated", {"strategy": strategy, "version": version})
        return strategy

    def deploy(self, strategy: Strategy, target: str) -> StrategyDeployment:
        deployment = StrategyDeployment(target=target, status="Deployed", deployed_at="now", broker_interface="Broker Interface", orchestrator="Application Orchestrator")
        strategy.deployment = deployment
        self._publish("StrategyDeployed", {"strategy": strategy, "deployment": deployment})
        if self.broker is not None:
            trade = Trade(symbol="AAPL", direction="BUY", quantity=10, entry_price=100.0)
            result = self.broker.execute(trade)
            if not result.success:
                deployment.status = "Failed"
        return deployment

    def archive(self, strategy: Strategy) -> Strategy:
        strategy.status = "Archived"
        self._publish("StrategyArchived", {"strategy": strategy})
        return strategy

    def refresh(self) -> None:
        self._refresh_count += 1

    def refresh_count(self) -> int:
        return self._refresh_count

    def subscribe(self, event_name: str, handler: Any) -> None:
        self.event_bus.subscribe(event_name, handler)

    def _publish(self, event_name: str, payload: dict[str, Any]) -> None:
        self._events.append(event_name)
        self.event_bus.publish(event_name, payload)

    def _seed_default_strategy(self) -> None:
        configuration = StrategyConfiguration(
            rsi_period=14,
            rsi_buy_level=30.0,
            rsi_sell_level=70.0,
            ema_fast=9,
            ema_slow=21,
            risk_per_trade=0.01,
            max_positions=3,
            reward_risk=2.0,
            stop_loss=0.02,
            take_profit=0.04,
            execution_mode="Paper",
        )
        performance = StrategyPerformance(backtest_return=12.4, paper_return=4.8, live_return=0.0, win_rate=0.62, profit_factor=1.85, sharpe_ratio=1.21, max_drawdown=0.08, total_trades=128)
        version = StrategyVersion(version="1.0.0", date="2026-07-31", author="TradePilotAI", notes="Initial release")
        version.configuration = configuration
        version.performance = performance
        strategy = Strategy(
            name="Momentum Pulse",
            version="1.0.0",
            description="EMA and RSI based momentum strategy",
            status="Paper Trading",
            markets="FX, Indices",
            timeframe="15M",
            created_date="2026-07-10",
            last_modified="2026-07-31",
            configuration=configuration,
            performance=performance,
            versions=[version],
        )
        self._strategies.append(strategy)
