"""Paper trading position monitor."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from tradepilotai_os.market_data import MarketDataProvider
from tradepilotai_os.market_data import YahooMarketDataProvider

from .engine import PaperPortfolioEngine


class PositionMonitor:
    """Refresh open paper positions from live market data."""

    def __init__(self, portfolio_engine: PaperPortfolioEngine, market_data_provider: MarketDataProvider | None = None) -> None:
        self.portfolio_engine = portfolio_engine
        self.market_data_provider = market_data_provider or YahooMarketDataProvider()

    def refresh(self) -> dict[str, Any]:
        refreshed_positions: list[dict[str, Any]] = []
        failed_symbols: list[dict[str, Any]] = []

        open_positions = self.portfolio_engine.get_open_positions()
        if not open_positions:
            self.portfolio_engine.refresh_portfolio()
            self.portfolio_engine.record_audit_event(
                "PORTFOLIO_UPDATED",
                timestamp=self._utc_now(),
                reason="No open positions to refresh.",
            )
            self.portfolio_engine.record_audit_event(
                "STATISTICS_UPDATED",
                timestamp=self._utc_now(),
                reason="No open positions to refresh.",
            )
            return self._build_result(refreshed_positions, failed_symbols)

        for position in open_positions:
            refreshed = self.refresh_position(position.symbol)
            if refreshed is None:
                failed_symbols.append({"symbol": position.symbol, "reason": "Price lookup failed."})
                continue
            refreshed_positions.append(asdict(refreshed))

        self.portfolio_engine.refresh_portfolio()
        self.portfolio_engine.record_audit_event(
            "PORTFOLIO_UPDATED",
            timestamp=self._utc_now(),
            reason="Position monitor refresh completed.",
        )
        self.portfolio_engine.record_audit_event(
            "STATISTICS_UPDATED",
            timestamp=self._utc_now(),
            reason="Position monitor refresh completed.",
        )

        return self._build_result(refreshed_positions, failed_symbols)

    def refresh_position(self, symbol: str) -> Any:
        position = self.portfolio_engine.get_open_position(symbol)
        if position is None:
            return None

        old_price = float(position.current_price or position.entry_price or 0.0)
        try:
            quote = self.market_data_provider.quote(symbol)
        except Exception as error:
            self._mark_stale(position, reason=f"Quote lookup failed: {error}")
            self.portfolio_engine.record_audit_event(
                "MARKET_PRICE_UPDATED",
                timestamp=self._utc_now(),
                position_id=position.position_id,
                symbol=position.symbol,
                old_price=old_price,
                new_price=old_price,
                reason="Quote lookup failed.",
            )
            return None

        current_price = self._extract_price(quote)
        if current_price is None:
            self._mark_stale(position, reason="Quote did not include a usable price.")
            self.portfolio_engine.record_audit_event(
                "MARKET_PRICE_UPDATED",
                timestamp=self._utc_now(),
                position_id=position.position_id,
                symbol=position.symbol,
                old_price=old_price,
                new_price=old_price,
                reason="Quote did not include a usable price.",
            )
            return None

        self.portfolio_engine.update_market_price(symbol, current_price)
        position = self.portfolio_engine.get_open_position(symbol)
        if position is None:
            return None

        self._update_position_metadata(position, current_price=current_price, quote=quote)
        self.portfolio_engine.record_audit_event(
            "MARKET_PRICE_UPDATED",
            timestamp=self._utc_now(),
            position_id=position.position_id,
            symbol=position.symbol,
            old_price=old_price,
            new_price=current_price,
            reason="Live market quote received.",
        )
        self.portfolio_engine.record_audit_event(
            "POSITION_MARKED_TO_MARKET",
            timestamp=self._utc_now(),
            position_id=position.position_id,
            symbol=position.symbol,
            old_price=old_price,
            new_price=current_price,
            reason="Position marked to market.",
        )
        return position

    def refresh_all_positions(self) -> list[Any]:
        return self.refresh().get("refreshed_positions", [])

    def _update_position_metadata(self, position: Any, *, current_price: float, quote: Any) -> None:
        now = datetime.now(timezone.utc)
        entry_price = float(getattr(position, "entry_price", 0.0) or 0.0)
        quantity = int(getattr(position, "quantity", 0) or 0)
        stop_loss = float(getattr(position, "stop_loss", 0.0) or 0.0)
        target = float(getattr(position, "target", 0.0) or 0.0)
        direction = str(getattr(position, "direction", "BUY") or "BUY").upper()
        quote_open = self._extract_float(quote, "open")

        todays_change = current_price - quote_open if quote_open is not None else 0.0
        todays_change_percent = (todays_change / quote_open) * 100.0 if quote_open else 0.0
        unrealised_pnl = float(getattr(position, "unrealised_pnl", 0.0) or 0.0)
        unrealised_pnl_percent = (unrealised_pnl / (entry_price * quantity)) * 100.0 if entry_price and quantity else 0.0

        if direction == "SELL":
            distance_to_stop = stop_loss - current_price
            distance_to_target = current_price - target
        else:
            distance_to_stop = current_price - stop_loss
            distance_to_target = target - current_price

        setattr(position, "todays_change", round(todays_change, 2))
        setattr(position, "todays_change_percent", round(todays_change_percent, 2))
        setattr(position, "unrealised_pnl_percent", round(unrealised_pnl_percent, 2))
        setattr(position, "distance_to_stop_loss", round(distance_to_stop, 2))
        setattr(position, "distance_to_target", round(distance_to_target, 2))
        setattr(position, "current_risk", round(max(0.0, distance_to_stop) * quantity, 2))
        setattr(position, "days_open", self._days_open(getattr(position, "entry_date", None), now))
        setattr(position, "last_updated", now.isoformat(timespec="seconds"))
        setattr(position, "price_status", "LIVE")
        setattr(position, "price_stale", False)

    def _mark_stale(self, position: Any, *, reason: str) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        setattr(position, "price_status", "STALE")
        setattr(position, "price_stale", True)
        setattr(position, "last_updated", now)
        self.portfolio_engine.record_audit_event(
            "MARKET_PRICE_UPDATE_FAILED",
            timestamp=now,
            position_id=position.position_id,
            symbol=position.symbol,
            old_price=float(getattr(position, "current_price", 0.0) or 0.0),
            new_price=float(getattr(position, "current_price", 0.0) or 0.0),
            reason=reason,
        )

    def _extract_price(self, quote: Any) -> float | None:
        value = self._extract_float(quote, "price")
        if value is not None:
            return value
        if isinstance(quote, dict):
            return self._extract_float(quote, "lastPrice")
        return None

    def _extract_float(self, quote: Any, key: str) -> float | None:
        value: Any = None
        if isinstance(quote, dict):
            value = quote.get(key)
        else:
            value = getattr(quote, key, None)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _days_open(self, entry_date: Any, now: datetime) -> int:
        if not entry_date:
            return 0
        try:
            parsed = datetime.fromisoformat(str(entry_date))
        except ValueError:
            return 0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return max(0, (now - parsed.astimezone(timezone.utc)).days)

    def _build_result(self, refreshed_positions: list[dict[str, Any]], failed_symbols: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "refreshed_positions": refreshed_positions,
            "failed_symbols": failed_symbols,
            "summary": self.portfolio_engine.get_summary(),
            "statistics": asdict(self.portfolio_engine.get_statistics()),
            "audit_events": self.portfolio_engine.get_audit_events(),
        }

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")