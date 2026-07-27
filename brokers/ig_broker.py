"""
===========================================================
TradePilotAI
IG Broker
===========================================================

Live broker implementation using IG Markets.
"""

from __future__ import annotations

from brokers.broker import Broker
from brokers.ig_client import IGClient

from models.position import Position
from models.trade import Trade
from models.trade_order import TradeOrder

from signals.signal_types import SignalType


class IGBroker(Broker):
    """
    IG Markets broker implementation.
    """

    def __init__(
        self,
        client: IGClient,
    ) -> None:

        self._client = client

        self._deal_ids: dict[str, str] = {}


    def execute(
        self,
        order: TradeOrder,
        position: Position | None = None,
    ) -> Position | Trade:

        if order.action == SignalType.BUY:

            return self._execute_buy(order)


        if order.action == SignalType.SELL:

            if position is None:
                raise ValueError(
                    "SELL orders require an existing Position."
                )

            return self._execute_sell(
                order,
                position,
            )


        raise ValueError(
            f"Unsupported order action: {order.action}"
        )


    def _execute_buy(
        self,
        order: TradeOrder,
    ) -> Position:

        response = self._client.open_position(
            epic=order.symbol,
            direction="BUY",
            size=order.quantity,
            stop_distance=order.stop_loss,
            limit_distance=order.take_profit,
        )


        deal_id = response.get(
            "dealId"
        )


        if deal_id:

            self._deal_ids[
                order.symbol
            ] = deal_id


        return Position(
            symbol=order.symbol,
            quantity=order.quantity,
            entry_price=order.price,
            current_price=order.price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            strategy=order.strategy,
        )


    def _execute_sell(
        self,
        order: TradeOrder,
        position: Position,
    ) -> Trade:

        deal_id = self._deal_ids.get(
            position.symbol
        )


        if deal_id is None:
            raise ValueError(
                f"No IG deal found for {position.symbol}."
            )


        self._client.close_position(
            deal_id
        )


        return Trade(
            symbol=position.symbol,
            quantity=position.quantity,
            entry_price=position.entry_price,
            exit_price=order.price,
            entry_date=position.entry_date,
            exit_date=order.timestamp,
            strategy=position.strategy,
        )