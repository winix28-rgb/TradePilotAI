"""Trade approval queue for scanner-generated signals."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.broker.base import Broker
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk.risk_engine import RiskEngine


class TradeApprovalQueue:
    """Hold pending scanner signals until they are approved or rejected."""

    def __init__(
        self,
        portfolio_manager: PortfolioManager | None = None,
        broker: Broker | None = None,
        risk_engine: RiskEngine | None = None,
        pending_trades: list[TradeSignal] | None = None,
    ) -> None:
        self.portfolio_manager = portfolio_manager
        self.broker = broker
        self.risk_engine = risk_engine
        self.pending_trades: list[TradeSignal] = list(pending_trades or [])
        self.approved_trades: list[TradeSignal] = []
        self.rejected_trades: list[TradeSignal] = []
        self.last_action: dict[str, Any] | None = None

    def load_from_scan_results(self, scan_results: dict[str, Any] | None = None) -> list[TradeSignal]:
        """Populate the approval queue using scan payloads that still contain TradeSignal objects."""
        if scan_results is None:
            return list(self.pending_trades)

        rows = scan_results.get("results", []) if isinstance(scan_results, dict) else []
        if not isinstance(rows, list):
            rows = []

        for row in rows:
            if isinstance(row, TradeSignal):
                signal = row
            elif isinstance(row, dict):
                signal = row.get("raw")
                if not isinstance(signal, TradeSignal):
                    continue
            else:
                continue

            if self._is_duplicate_signal(signal):
                continue

            strategy_name = str(row.get("strategy_name") or getattr(signal, "strategy_name", "TradePilotAI RSI Mean Reversion"))
            strategy_id = str(row.get("strategy_id") or getattr(signal, "strategy_id", "") or self._strategy_id_from_name(strategy_name))
            decision_id = str(row.get("decision_id") or row.get("decision") or getattr(signal, "decision_id", "") or "")

            setattr(signal, "strategy_name", strategy_name)
            setattr(signal, "strategy_id", strategy_id)
            setattr(signal, "decision_id", decision_id)
            self.pending_trades.append(signal)

        return list(self.pending_trades)

    def approve_trade(self, trade_or_signal: TradeSignal | Trade | Any) -> dict[str, Any]:
        """Validate a pending signal and execute it through the broker if approved."""
        signal = self._coerce_signal(trade_or_signal)
        if signal is None:
            return {"approved": False, "reason": "No trade signal was supplied."}

        if signal not in self.pending_trades:
            self.pending_trades.append(signal)

        trade = self._build_trade(signal)
        validation = self._validate_trade(trade, signal)
        if not validation["allowed"]:
            self.last_action = {"action": "approve", "approved": False, "reason": validation["reason"]}
            return {"approved": False, **validation}

        self._prepare_execution(signal, trade, validation)
        result = self.broker.execute(trade) if self.broker is not None else None
        if result is not None and not getattr(result, "success", False):
            reason = getattr(result, "message", "Broker rejected the trade.")
            self.last_action = {"action": "approve", "approved": False, "reason": reason}
            return {"approved": False, "reason": reason}

        self.pending_trades = [item for item in self.pending_trades if item is not signal]
        self.approved_trades.append(signal)
        self.last_action = {"action": "approve", "approved": True, "reason": "Trade approved and sent to broker."}
        return {"approved": True, "reason": "Trade approved and sent to broker.", "trade": trade, "execution_result": result}

    def reject_trade(self, trade_or_signal: TradeSignal | Trade | Any) -> dict[str, Any]:
        """Remove a pending signal from the approval queue."""
        signal = self._coerce_signal(trade_or_signal)
        if signal is None:
            return {"approved": False, "reason": "No trade signal was supplied."}

        self.pending_trades = [item for item in self.pending_trades if item is not signal]
        self.rejected_trades.append(signal)
        self.last_action = {"action": "reject", "approved": False, "reason": "Trade rejected."}
        return {"approved": False, "reason": "Trade rejected."}

    def modify_trade(self, trade_or_signal: TradeSignal | Trade | Any, updates: dict[str, Any] | None = None) -> dict[str, Any]:
        """Update a pending trade signal before approval without executing it."""
        signal = self._coerce_signal(trade_or_signal)
        if signal is None:
            return {"approved": False, "reason": "No trade signal was supplied."}

        updates = updates or {}
        for key, value in updates.items():
            if key == "price":
                setattr(signal, "price", float(value))
            elif key == "stop_loss":
                setattr(signal, "stop_loss", float(value))
            elif key == "target":
                setattr(signal, "target", float(value))
            elif key == "confidence":
                setattr(signal, "confidence", int(value))
            elif key == "reason":
                if isinstance(value, str):
                    setattr(signal, "reasons", [value])
            elif key == "strategy_name":
                setattr(signal, "strategy_name", str(value))

        self.last_action = {"action": "modify", "approved": False, "reason": "Trade values updated."}
        return {"approved": False, "reason": "Trade values updated.", "signal": signal}

    def _validate_trade(self, trade: Trade, signal: TradeSignal) -> dict[str, Any]:
        if self.risk_engine is not None:
            assessment = self.risk_engine.assess_trade(trade)
            if not getattr(assessment, "permitted", False):
                return {"allowed": False, "reason": getattr(assessment, "reason", "Risk validation failed."), "trade": trade}

        if trade.quantity is None or trade.quantity <= 0:
            return {"allowed": False, "reason": "Trade quantity must be positive.", "trade": trade}

        if self.risk_engine is not None and self.risk_engine.max_position_size is not None:
            if trade.quantity > int(self.risk_engine.max_position_size):
                return {"allowed": False, "reason": "Maximum position size exceeded.", "trade": trade}

        if self.portfolio_manager is not None:
            position = self.portfolio_manager.get_position(signal.symbol)
            if position is not None and getattr(position, "quantity", 0) > 0:
                return {"allowed": False, "reason": "Duplicate position already exists.", "trade": trade}

            exposure = float(getattr(self.portfolio_manager.state, "exposure", 0.0) or 0.0)
            if exposure > 0.0 and exposure + (float(trade.entry_price or 0.0) * float(trade.quantity or 0)) > self._max_portfolio_risk():
                return {"allowed": False, "reason": "Portfolio exposure exceeds maximum portfolio risk.", "trade": trade}

        return {"allowed": True, "reason": "Trade passed validation.", "trade": trade}

    def _build_trade(self, signal: TradeSignal) -> Trade:
        return Trade(
            ticker=signal.symbol,
            direction=signal.signal.upper(),
            entry_time=None,
            entry_price=float(signal.price),
            stop_loss=float(signal.stop_loss),
            quantity=1,
            take_profit=float(signal.target),
            status="PENDING",
        )

    def _prepare_execution(self, signal: TradeSignal, trade: Trade, validation: dict[str, Any]) -> None:
        prepare_execution = getattr(self.broker, "prepare_execution", None)
        if not callable(prepare_execution):
            return

        strategy_name = str(getattr(signal, "strategy_name", "RSI Mean Reversion") or "RSI Mean Reversion")
        strategy_id = str(getattr(signal, "strategy_id", "") or self._strategy_id_from_name(strategy_name))
        decision_id = str(getattr(signal, "decision_id", "") or getattr(signal, "signal", "") or "APPROVE")
        reason = str(validation.get("reason") or "; ".join(getattr(signal, "reasons", []) or []) or "Approved trade")

        try:
            prepare_execution(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                decision_id=decision_id,
                reason=reason,
                risk_assessment=validation.get("risk_assessment"),
            )
        except TypeError:
            prepare_execution(
                strategy_name=strategy_name,
                decision=decision_id,
                reason=reason,
                risk_assessment=validation.get("risk_assessment"),
            )

    def _coerce_signal(self, trade_or_signal: Any) -> TradeSignal | None:
        if isinstance(trade_or_signal, TradeSignal):
            return trade_or_signal
        if isinstance(trade_or_signal, Trade):
            return None
        if hasattr(trade_or_signal, "symbol") and hasattr(trade_or_signal, "signal"):
            return trade_or_signal
        return None

    def _is_duplicate_signal(self, signal: TradeSignal) -> bool:
        return any(getattr(item, "symbol", None) == signal.symbol for item in self.pending_trades)

    def _max_portfolio_risk(self) -> float:
        if self.risk_engine is None:
            return 1000000.0
        return float(getattr(self.risk_engine, "account_balance", 100000.0) * getattr(self.risk_engine, "risk_per_trade", 0.01) * 10.0)

    def _strategy_id_from_name(self, strategy_name: str) -> str:
        text = str(strategy_name or "").strip().lower()
        if not text:
            return "rsi_mean_reversion"
        if text.startswith("tradepilotai "):
            text = text.removeprefix("tradepilotai ").strip()
        return "".join(character if character.isalnum() else "_" for character in text).strip("_") or "rsi_mean_reversion"
