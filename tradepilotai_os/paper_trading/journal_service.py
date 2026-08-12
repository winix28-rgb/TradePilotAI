"""Event-driven Trade Journal service for paper trading."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from datetime import date
from datetime import datetime
from datetime import timezone
from itertools import count
from xml.sax.saxutils import escape

from .journal_models import DecisionSnapshot
from .journal_models import JournalEntry
from .journal_models import MarketSnapshot
from .journal_models import PerformanceSnapshot
from .journal_models import RiskSnapshot


class TradeJournal:
    """Immutable journal storage with deduplication by trade id."""

    def __init__(self) -> None:
        self._ids = count(1)
        self._entries: list[JournalEntry] = []
        self._entry_by_journal_id: dict[str, JournalEntry] = {}
        self._journal_id_by_trade_id: dict[str, str] = {}

    def add(self, entry: JournalEntry) -> bool:
        if entry.trade_id in self._journal_id_by_trade_id:
            return False
        self._entries.append(entry)
        self._entry_by_journal_id[entry.journal_id] = entry
        self._journal_id_by_trade_id[entry.trade_id] = entry.journal_id
        return True

    def next_journal_id(self) -> str:
        return f"JRN-{next(self._ids):05d}"

    def exists_trade(self, trade_id: str) -> bool:
        return trade_id in self._journal_id_by_trade_id

    def get(self, journal_id: str) -> JournalEntry | None:
        return self._entry_by_journal_id.get(journal_id)

    def entries(self) -> list[JournalEntry]:
        return list(self._entries)


class JournalService:
    """Consumes TRADE_JOURNAL_EVENT records and exposes journal operations."""

    TRADE_EVENT_NAME = "TRADE_JOURNAL_EVENT"

    def __init__(self) -> None:
        self.journal = TradeJournal()
        self._processed_event_keys: set[str] = set()
        self._notes_by_journal_id: dict[str, str] = {}

    def consume_events(self, events: list[dict]) -> int:
        created = 0
        for event in events or []:
            created += self.consume_event(event)
        return created

    def consume_event(self, event: dict) -> int:
        if not isinstance(event, dict):
            return 0
        if str(event.get("event", "")) != self.TRADE_EVENT_NAME:
            return 0

        details = event.get("details", {}) or {}
        trade_id = str(details.get("trade_id", "") or "")
        position_id = str(details.get("position_id", "") or "")
        timestamp = str(event.get("timestamp", "") or "")

        if not trade_id:
            return 0

        event_key = f"{trade_id}|{position_id}|{timestamp}"
        if event_key in self._processed_event_keys:
            return 0
        self._processed_event_keys.add(event_key)

        if self.journal.exists_trade(trade_id):
            return 0

        payload = details.get("payload", {}) or {}
        entry = self._build_entry(payload=payload, event=event)
        if self.journal.add(entry):
            return 1
        return 0

    def get_entries(
        self,
        *,
        filters: dict | None = None,
        search: str = "",
        sort_by: str = "exit_date",
        ascending: bool = False,
    ) -> list[dict]:
        entries = [self._entry_payload(entry) for entry in self.journal.entries()]
        filtered = self._apply_filters(entries, filters or {})
        searched = self._apply_search(filtered, search)
        return self._sort_entries(searched, sort_by=sort_by, ascending=ascending)

    def get_summary(self, entries: list[dict] | None = None) -> dict:
        rows = entries if entries is not None else self.get_entries()
        total = len(rows)
        winners = [row for row in rows if float(row.get("net_profit", 0.0) or 0.0) > 0]
        losers = [row for row in rows if float(row.get("net_profit", 0.0) or 0.0) < 0]
        winner_values = [float(row.get("net_profit", 0.0) or 0.0) for row in winners]
        loser_values = [float(row.get("net_profit", 0.0) or 0.0) for row in losers]
        net_profit = round(sum(float(row.get("net_profit", 0.0) or 0.0) for row in rows), 2)

        return {
            "total_trades": total,
            "winners": len(winners),
            "losers": len(losers),
            "win_rate": round((len(winners) / total) * 100.0, 2) if total else 0.0,
            "net_profit": net_profit,
            "average_winner": round(sum(winner_values) / len(winner_values), 2) if winner_values else 0.0,
            "average_loser": round(sum(loser_values) / len(loser_values), 2) if loser_values else 0.0,
            "largest_winner": round(max(winner_values), 2) if winner_values else 0.0,
            "largest_loser": round(min(loser_values), 2) if loser_values else 0.0,
        }

    def get_trade_detail(self, journal_id: str) -> dict:
        entry = self.journal.get(journal_id)
        if entry is None:
            return {}
        return self._entry_payload(entry)

    def set_note(self, journal_id: str, note: str) -> bool:
        if self.journal.get(journal_id) is None:
            return False
        self._notes_by_journal_id[journal_id] = str(note)
        return True

    def get_note(self, journal_id: str) -> str:
        return self._notes_by_journal_id.get(journal_id, "")

    def export(self, *, format_name: str, entries: list[dict] | None = None) -> tuple[bytes, str, str]:
        rows = entries if entries is not None else self.get_entries()
        flat_rows = [self._flatten_for_export(row) for row in rows]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if format_name.lower() == "csv":
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=self._export_columns())
            writer.writeheader()
            writer.writerows(flat_rows)
            data = buffer.getvalue().encode("utf-8")
            return data, f"trade_journal_{timestamp}.csv", "text/csv"

        if format_name.lower() in {"excel", "xlsx"}:
            xml = self._build_excel_xml(flat_rows)
            return xml.encode("utf-8"), f"trade_journal_{timestamp}.xls", "application/vnd.ms-excel"

        data = json.dumps(flat_rows, indent=2).encode("utf-8")
        return data, f"trade_journal_{timestamp}.json", "application/json"

    def _build_entry(self, *, payload: dict, event: dict) -> JournalEntry:
        trade_id = str(payload.get("trade_id", "") or "")
        entry_price = float(payload.get("entry_price", 0.0) or 0.0)
        exit_price = float(payload.get("exit_price", 0.0) or 0.0)
        quantity = int(payload.get("quantity", 0) or 0)
        gross_profit = float(payload.get("gross_profit", 0.0) or 0.0)
        costs = float(payload.get("costs", 0.0) or 0.0)
        net_profit = float(payload.get("net_profit", 0.0) or 0.0)
        direction = str(payload.get("direction", "BUY") or "BUY").upper()
        return_percent = 0.0
        basis = entry_price * quantity
        if basis > 0:
            return_percent = round((net_profit / basis) * 100.0, 4)

        decision_raw = payload.get("decision_snapshot", {}) or {}
        reasons = decision_raw.get("reasons", []) or []
        decision_snapshot = DecisionSnapshot(
            decision_score=float(decision_raw.get("decision_score", 0.0) or 0.0),
            confidence=float(decision_raw.get("confidence", 0.0) or 0.0),
            technical_score=float(decision_raw.get("technical_score", 0.0) or 0.0),
            strategy_score=float(decision_raw.get("strategy_score", 0.0) or 0.0),
            risk_score=float(decision_raw.get("risk_score", 0.0) or 0.0),
            portfolio_score=float(decision_raw.get("portfolio_score", 0.0) or 0.0),
            market_score=float(decision_raw.get("market_score", 0.0) or 0.0),
            reasons=tuple(str(item) for item in reasons),
        )

        risk_raw = payload.get("risk_snapshot", {}) or {}
        risk_snapshot = RiskSnapshot(
            risk_percent=float(risk_raw.get("risk_percent", 0.0) or 0.0),
            position_size=float(risk_raw.get("position_size", 0.0) or 0.0),
            capital_at_risk=float(risk_raw.get("capital_at_risk", 0.0) or 0.0),
            reward_risk_ratio=float(risk_raw.get("reward_risk_ratio", 0.0) or 0.0),
            stop_loss=float(risk_raw.get("stop_loss", 0.0) or 0.0),
            target=float(risk_raw.get("target", 0.0) or 0.0),
        )

        performance_raw = payload.get("performance_snapshot", {}) or {}
        performance_snapshot = PerformanceSnapshot(
            win_loss=str(performance_raw.get("win_loss", "LOSS") or "LOSS"),
            profit_factor_at_trade_time=float(performance_raw.get("profit_factor_at_trade_time", 0.0) or 0.0),
            running_equity=float(performance_raw.get("running_equity", 0.0) or 0.0),
            running_drawdown=float(performance_raw.get("running_drawdown", 0.0) or 0.0),
            strategy_win_rate=float(performance_raw.get("strategy_win_rate", 0.0) or 0.0),
            portfolio_win_rate=float(performance_raw.get("portfolio_win_rate", 0.0) or 0.0),
        )

        market_raw = payload.get("market_snapshot", {}) or {}
        market_snapshot = MarketSnapshot(
            timeframe=str(market_raw.get("timeframe", "") or ""),
            trend=str(market_raw.get("trend", "") or ""),
            rsi=self._optional_float(market_raw.get("rsi")),
            ema12=self._optional_float(market_raw.get("ema12")),
            ema26=self._optional_float(market_raw.get("ema26")),
            macd=self._optional_float(market_raw.get("macd")),
            atr=self._optional_float(market_raw.get("atr")),
            volume=self._optional_float(market_raw.get("volume")),
            indicators=dict(market_raw.get("indicators", {}) or {}),
        )

        tags = tuple(self._assign_tags(payload=payload, direction=direction, net_profit=net_profit))
        evidence = tuple(str(item) for item in (payload.get("supporting_evidence", []) or []))
        audit_events = tuple((payload.get("audit_events", []) or []))

        return JournalEntry(
            journal_id=self.journal.next_journal_id(),
            trade_id=trade_id,
            position_id=str(payload.get("position_id", "") or ""),
            decision_id=str(payload.get("decision_id", "") or ""),
            strategy_id=str(payload.get("strategy_id", "") or ""),
            strategy_name=str(payload.get("strategy_name", "") or ""),
            symbol=str(payload.get("symbol", "") or ""),
            asset_class=str(payload.get("asset_class", "EQUITY") or "EQUITY"),
            direction=direction,
            entry_date=str(payload.get("entry_date", "") or ""),
            exit_date=str(payload.get("exit_date", event.get("timestamp", "")) or ""),
            holding_period=str(payload.get("holding_period", "0 days") or "0 days"),
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            gross_profit=gross_profit,
            costs=costs,
            net_profit=net_profit,
            return_percent=return_percent,
            exit_reason=str(payload.get("exit_reason", "") or ""),
            exit_explanation=str(payload.get("exit_explanation", "") or ""),
            decision_snapshot=decision_snapshot,
            risk_snapshot=risk_snapshot,
            performance_snapshot=performance_snapshot,
            market_snapshot=market_snapshot,
            tags=tags,
            supporting_evidence=evidence,
            audit_events=audit_events,
        )

    def _entry_payload(self, entry: JournalEntry) -> dict:
        payload = asdict(entry)
        payload["notes"] = self.get_note(entry.journal_id)
        payload["winner"] = entry.net_profit > 0
        payload["loser"] = entry.net_profit < 0
        return payload

    def _apply_filters(self, entries: list[dict], filters: dict) -> list[dict]:
        start_date = self._parse_date(str(filters.get("start_date", "") or ""))
        end_date = self._parse_date(str(filters.get("end_date", "") or ""))
        strategy = str(filters.get("strategy", "") or "").strip()
        symbol = str(filters.get("symbol", "") or "").strip().upper()
        direction = str(filters.get("direction", "") or "").strip().upper()
        exit_reason = str(filters.get("exit_reason", "") or "").strip().upper()
        winner_filter = filters.get("winner")
        loser_filter = filters.get("loser")

        result = []
        for row in entries:
            if start_date or end_date:
                exit_dt = self._parse_date(str(row.get("exit_date", "") or ""))
                if exit_dt is None:
                    continue
                if start_date and exit_dt < start_date:
                    continue
                if end_date and exit_dt > end_date:
                    continue

            if strategy and str(row.get("strategy_id", "")).strip() != strategy and str(row.get("strategy_name", "")).strip() != strategy:
                continue
            if symbol and str(row.get("symbol", "")).upper() != symbol:
                continue
            if direction and str(row.get("direction", "")).upper() != direction:
                continue
            if exit_reason and str(row.get("exit_reason", "")).upper() != exit_reason:
                continue

            if winner_filter is True and not bool(row.get("winner", False)):
                continue
            if loser_filter is True and not bool(row.get("loser", False)):
                continue

            result.append(row)
        return result

    def _apply_search(self, entries: list[dict], search: str) -> list[dict]:
        query = str(search or "").strip().lower()
        if not query:
            return entries

        result = []
        for row in entries:
            haystack = " ".join(
                [
                    str(row.get("journal_id", "")),
                    str(row.get("trade_id", "")),
                    str(row.get("position_id", "")),
                    str(row.get("decision_id", "")),
                    str(row.get("strategy_id", "")),
                    str(row.get("strategy_name", "")),
                    str(row.get("symbol", "")),
                    str(row.get("direction", "")),
                    str(row.get("exit_reason", "")),
                    str(row.get("exit_explanation", "")),
                    str(row.get("tags", "")),
                    str(row.get("notes", "")),
                ]
            ).lower()
            if query in haystack:
                result.append(row)
        return result

    def _sort_entries(self, entries: list[dict], *, sort_by: str, ascending: bool) -> list[dict]:
        key_name = str(sort_by or "exit_date")

        def key_func(item: dict):
            value = item.get(key_name)
            if isinstance(value, str):
                dt = self._parse_datetime(value)
                if dt is not None:
                    return dt
                return value.lower()
            return value

        return sorted(entries, key=key_func, reverse=not ascending)

    def _assign_tags(self, *, payload: dict, direction: str, net_profit: float) -> list[str]:
        tags: list[str] = []

        if net_profit > 0:
            tags.append("Winner")
            if net_profit >= 500.0:
                tags.append("Large Winner")
        elif net_profit < 0:
            tags.append("Loser")
            if net_profit <= -500.0:
                tags.append("Large Loser")

        strategy_name = str(payload.get("strategy_name", "") or "").lower()
        strategy_id = str(payload.get("strategy_id", "") or "").lower()
        if "mean" in strategy_name or "mean" in strategy_id or "rsi" in strategy_id:
            tags.append("Mean Reversion")
        if "trend" in strategy_name or "trend" in strategy_id or "ema" in strategy_id:
            tags.append("Trend Following")

        if direction == "SELL":
            tags.append("Short")
        else:
            tags.append("Long")

        reason = str(payload.get("exit_reason", "") or "").upper()
        mapping = {
            "STOP_LOSS": "Stop Loss",
            "TAKE_PROFIT": "Take Profit",
            "STRATEGY_EXIT": "Strategy Exit",
            "MANUAL_EXIT": "Manual Exit",
        }
        if reason in mapping:
            tags.append(mapping[reason])

        return sorted(set(tags))

    def _optional_float(self, value):
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _parse_datetime(self, value: str) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _parse_date(self, value: str) -> date | None:
        dt = self._parse_datetime(value)
        if dt is not None:
            return dt.date()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    def _flatten_for_export(self, row: dict) -> dict:
        flattened = {
            "journal_id": row.get("journal_id", ""),
            "trade_id": row.get("trade_id", ""),
            "position_id": row.get("position_id", ""),
            "decision_id": row.get("decision_id", ""),
            "strategy_id": row.get("strategy_id", ""),
            "strategy_name": row.get("strategy_name", ""),
            "symbol": row.get("symbol", ""),
            "asset_class": row.get("asset_class", ""),
            "direction": row.get("direction", ""),
            "entry_date": row.get("entry_date", ""),
            "exit_date": row.get("exit_date", ""),
            "holding_period": row.get("holding_period", ""),
            "entry_price": row.get("entry_price", 0.0),
            "exit_price": row.get("exit_price", 0.0),
            "quantity": row.get("quantity", 0),
            "gross_profit": row.get("gross_profit", 0.0),
            "costs": row.get("costs", 0.0),
            "net_profit": row.get("net_profit", 0.0),
            "return_percent": row.get("return_percent", 0.0),
            "exit_reason": row.get("exit_reason", ""),
            "exit_explanation": row.get("exit_explanation", ""),
            "tags": ", ".join(row.get("tags", [])),
            "notes": row.get("notes", ""),
        }

        decision_snapshot = row.get("decision_snapshot", {}) or {}
        risk_snapshot = row.get("risk_snapshot", {}) or {}
        performance_snapshot = row.get("performance_snapshot", {}) or {}
        market_snapshot = row.get("market_snapshot", {}) or {}

        flattened.update(
            {
                "decision_score": decision_snapshot.get("decision_score", 0.0),
                "confidence": decision_snapshot.get("confidence", 0.0),
                "technical_score": decision_snapshot.get("technical_score", 0.0),
                "strategy_score": decision_snapshot.get("strategy_score", 0.0),
                "risk_score": decision_snapshot.get("risk_score", 0.0),
                "portfolio_score": decision_snapshot.get("portfolio_score", 0.0),
                "market_score": decision_snapshot.get("market_score", 0.0),
                "reasons": ", ".join(decision_snapshot.get("reasons", [])),
                "risk_percent": risk_snapshot.get("risk_percent", 0.0),
                "position_size": risk_snapshot.get("position_size", 0.0),
                "capital_at_risk": risk_snapshot.get("capital_at_risk", 0.0),
                "reward_risk_ratio": risk_snapshot.get("reward_risk_ratio", 0.0),
                "stop_loss": risk_snapshot.get("stop_loss", 0.0),
                "target": risk_snapshot.get("target", 0.0),
                "win_loss": performance_snapshot.get("win_loss", "LOSS"),
                "profit_factor_at_trade_time": performance_snapshot.get("profit_factor_at_trade_time", 0.0),
                "running_equity": performance_snapshot.get("running_equity", 0.0),
                "running_drawdown": performance_snapshot.get("running_drawdown", 0.0),
                "strategy_win_rate": performance_snapshot.get("strategy_win_rate", 0.0),
                "portfolio_win_rate": performance_snapshot.get("portfolio_win_rate", 0.0),
                "timeframe": market_snapshot.get("timeframe", ""),
                "trend": market_snapshot.get("trend", ""),
                "rsi": market_snapshot.get("rsi", ""),
                "ema12": market_snapshot.get("ema12", ""),
                "ema26": market_snapshot.get("ema26", ""),
                "macd": market_snapshot.get("macd", ""),
                "atr": market_snapshot.get("atr", ""),
                "volume": market_snapshot.get("volume", ""),
                "indicators": json.dumps(market_snapshot.get("indicators", {}), ensure_ascii=True),
            }
        )
        return flattened

    def _export_columns(self) -> list[str]:
        return [
            "journal_id",
            "trade_id",
            "position_id",
            "decision_id",
            "strategy_id",
            "strategy_name",
            "symbol",
            "asset_class",
            "direction",
            "entry_date",
            "exit_date",
            "holding_period",
            "entry_price",
            "exit_price",
            "quantity",
            "gross_profit",
            "costs",
            "net_profit",
            "return_percent",
            "exit_reason",
            "exit_explanation",
            "tags",
            "notes",
            "decision_score",
            "confidence",
            "technical_score",
            "strategy_score",
            "risk_score",
            "portfolio_score",
            "market_score",
            "reasons",
            "risk_percent",
            "position_size",
            "capital_at_risk",
            "reward_risk_ratio",
            "stop_loss",
            "target",
            "win_loss",
            "profit_factor_at_trade_time",
            "running_equity",
            "running_drawdown",
            "strategy_win_rate",
            "portfolio_win_rate",
            "timeframe",
            "trend",
            "rsi",
            "ema12",
            "ema26",
            "macd",
            "atr",
            "volume",
            "indicators",
        ]

    def _build_excel_xml(self, rows: list[dict]) -> str:
        headers = self._export_columns()
        xml_rows = []

        header_cells = "".join(f"<Cell><Data ss:Type='String'>{escape(col)}</Data></Cell>" for col in headers)
        xml_rows.append(f"<Row>{header_cells}</Row>")

        for row in rows:
            cells: list[str] = []
            for col in headers:
                value = row.get(col, "")
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    cells.append(f"<Cell><Data ss:Type='Number'>{value}</Data></Cell>")
                else:
                    cells.append(f"<Cell><Data ss:Type='String'>{escape(str(value))}</Data></Cell>")
            xml_rows.append(f"<Row>{''.join(cells)}</Row>")

        return (
            "<?xml version='1.0'?>"
            "<?mso-application progid='Excel.Sheet'?>"
            "<Workbook xmlns='urn:schemas-microsoft-com:office:spreadsheet' "
            "xmlns:o='urn:schemas-microsoft-com:office:office' "
            "xmlns:x='urn:schemas-microsoft-com:office:excel' "
            "xmlns:ss='urn:schemas-microsoft-com:office:spreadsheet' "
            "xmlns:html='http://www.w3.org/TR/REC-html40'>"
            "<Worksheet ss:Name='Trade Journal'><Table>"
            + "".join(xml_rows)
            + "</Table></Worksheet></Workbook>"
        )
