"""Risk management engine for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from tradepilotai_os.models.trade import Trade


@dataclass(slots=True)
class RiskAssessment:
    """Represents the assessed risk for a proposed trade."""

    permitted: bool
    position_size: float = 1.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RiskEngine:
    """Evaluate proposed trades and attach risk management information.

    This layer consumes trade proposals from the strategy layer and
    decides whether they are permitted. It does not communicate with
    brokers or portfolio management systems.
    """

    def __init__(
        self,
        account_balance: float = 100000.0,
        risk_per_trade: float = 0.01,
        max_position_size: float = 1000.0,
    ) -> None:
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size

    def assess_trade(self, trade: Trade) -> RiskAssessment:
        """Evaluate a proposed trade and produce a risk assessment."""

        if trade.entry_price is None or trade.stop_loss is None:
            return RiskAssessment(
                permitted=False,
                reason="Trade is missing entry or stop-loss values.",
            )

        direction = trade.direction.upper()
        if direction not in {"BUY", "SELL"}:
            return RiskAssessment(
                permitted=False,
                reason="Trade direction must be BUY or SELL.",
            )

        stop_loss_distance = abs(trade.entry_price - trade.stop_loss)
        if stop_loss_distance <= 0:
            return RiskAssessment(
                permitted=False,
                position_size=0.0,
                stop_loss=trade.stop_loss,
                reason="Stop-loss is not valid for this entry price.",
            )

        if direction == "BUY" and trade.stop_loss >= trade.entry_price:
            return RiskAssessment(
                permitted=False,
                position_size=0.0,
                stop_loss=trade.stop_loss,
                reason="Stop-loss is not below the entry price.",
            )

        if direction == "SELL" and trade.stop_loss <= trade.entry_price:
            return RiskAssessment(
                permitted=False,
                position_size=0.0,
                stop_loss=trade.stop_loss,
                reason="Stop-loss is not above the entry price.",
            )

        risk_amount = self.account_balance * self.risk_per_trade
        quantity = int(risk_amount / stop_loss_distance)
        if quantity <= 0:
            quantity = 1

        if self.max_position_size is not None and self.max_position_size > 0:
            quantity = min(quantity, int(self.max_position_size))

        trade.quantity = quantity
        trade.take_profit = self._calculate_take_profit(trade)

        return RiskAssessment(
            permitted=True,
            position_size=float(quantity),
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            reason="Trade permitted under risk rules.",
            metadata={
                "risk_amount": risk_amount,
                "risk_distance": stop_loss_distance,
            },
        )

    def _calculate_take_profit(self, trade: Trade) -> float:
        """Compute a risk-based take-profit level for the trade."""

        distance = abs(trade.entry_price - trade.stop_loss)
        if trade.direction.upper() == "BUY":
            return trade.entry_price + (distance * 2)
        return trade.entry_price - (distance * 2)
