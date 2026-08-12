from __future__ import annotations

import json
from datetime import datetime, timezone

from tradepilotai_os.models.trade import Trade
from tradepilotai_os.paper_trading import ExitEngine
from tradepilotai_os.paper_trading import JournalDataProvider
from tradepilotai_os.paper_trading import JournalService
from tradepilotai_os.paper_trading import PaperPortfolioEngine
from tradepilotai_os.paper_trading import PaperTradingService


def _open_and_close_trade(
    *,
    service: PaperTradingService,
    symbol: str,
    direction: str,
    entry_price: float,
    stop_loss: float,
    quantity: int,
    exit_price: float,
    reason: str,
    explanation: str,
    strategy_id: str = "strategy-alpha",
    strategy_name: str = "Alpha Strategy",
    decision_id: str = "DEC-1",
):
    trade = Trade(
        ticker=symbol,
        direction=direction,
        entry_time=datetime.now(timezone.utc),
        entry_price=entry_price,
        stop_loss=stop_loss,
        quantity=quantity,
        take_profit=entry_price + abs(entry_price - stop_loss) * 2,
    )
    position = service.open_position(
        trade=trade,
        strategy_id=strategy_id,
        strategy_name=strategy_name,
        decision_id=decision_id,
        risk_assessment=None,
    )
    service.close_position(position.position_id, exit_price=exit_price, reason=reason)
    if explanation:
        service.manual_exit(position.position_id, reason=reason, explanation=explanation)


def _build_service() -> PaperTradingService:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    journal = JournalService()
    exit_engine = ExitEngine(portfolio_engine=engine)
    return PaperTradingService(portfolio_engine=engine, exit_engine=exit_engine, journal_service=journal)


def test_journal_event_creates_entry() -> None:
    service = _build_service()

    trade = Trade(
        ticker="AAPL",
        direction="BUY",
        entry_time=datetime.now(timezone.utc),
        entry_price=100.0,
        stop_loss=95.0,
        quantity=10,
        take_profit=110.0,
    )
    position = service.open_position(
        trade=trade,
        strategy_id="trend_alpha",
        strategy_name="Trend Alpha",
        decision_id="DEC-AAPL-1",
    )
    service.manual_exit(position.position_id, reason="MANUAL_EXIT", explanation="Operator override")

    payload = service.get_workspace_data()
    journal_payload = payload["trade_journal"]

    assert journal_payload["summary"]["total_trades"] == 1
    entry = journal_payload["entries"][0]
    assert entry["trade_id"].startswith("PT-")
    assert entry["position_id"] == position.position_id
    assert entry["decision_id"] == "DEC-AAPL-1"
    assert entry["symbol"] == "AAPL"
    assert entry["exit_reason"] == "MANUAL_EXIT"
    assert "Manual Exit" in entry["tags"]


def test_no_duplicate_journal_entries_from_repeat_reads() -> None:
    service = _build_service()

    trade = Trade(
        ticker="MSFT",
        direction="BUY",
        entry_time=datetime.now(timezone.utc),
        entry_price=200.0,
        stop_loss=190.0,
        quantity=5,
        take_profit=220.0,
    )
    position = service.open_position(
        trade=trade,
        strategy_id="trend_beta",
        strategy_name="Trend Beta",
        decision_id="DEC-MSFT-1",
    )
    service.manual_exit(position.position_id, reason="TAKE_PROFIT", explanation="Target met")

    first = service.get_workspace_data()["trade_journal"]["entries"]
    second = service.get_workspace_data()["trade_journal"]["entries"]

    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["trade_id"] == second[0]["trade_id"]


def test_filtering_sorting_and_search() -> None:
    service = _build_service()

    trades = [
        ("AAPL", "BUY", 100.0, 95.0, 10, 110.0, "TAKE_PROFIT", "TP hit", "trend_alpha", "Trend Alpha", "DEC-1"),
        ("TSLA", "BUY", 200.0, 195.0, 10, 190.0, "STOP_LOSS", "SL hit", "mean_alpha", "Mean Alpha", "DEC-2"),
        ("NVDA", "SELL", 300.0, 315.0, 8, 285.0, "STRATEGY_EXIT", "Signal exit", "trend_alpha", "Trend Alpha", "DEC-3"),
    ]

    for symbol, direction, entry, stop, qty, exit_p, reason, explanation, sid, sname, did in trades:
        trade = Trade(
            ticker=symbol,
            direction=direction,
            entry_time=datetime.now(timezone.utc),
            entry_price=entry,
            stop_loss=stop,
            quantity=qty,
            take_profit=entry + abs(entry - stop) * 2,
        )
        position = service.open_position(trade=trade, strategy_id=sid, strategy_name=sname, decision_id=did)
        service.close_position(position.position_id, exit_price=exit_p, reason=reason)

    provider = JournalDataProvider(journal_service=service.journal_service, paper_trading_service=service)
    all_rows = provider.get_trade_journal_data()["entries"]
    assert len(all_rows) == 3

    filtered = provider.get_trade_journal_data(filters={"symbol": "AAPL"})["entries"]
    assert len(filtered) == 1
    assert filtered[0]["symbol"] == "AAPL"

    filtered_winners = provider.get_trade_journal_data(filters={"winner": True})["entries"]
    assert all(row["winner"] for row in filtered_winners)

    searched = provider.get_trade_journal_data(search="strategy_exit")["entries"]
    assert len(searched) == 1
    assert searched[0]["symbol"] == "NVDA"

    sorted_rows = provider.get_trade_journal_data(sort_by="net_profit", ascending=False)["entries"]
    assert float(sorted_rows[0]["net_profit"]) >= float(sorted_rows[1]["net_profit"])


def test_export_formats() -> None:
    service = _build_service()

    trade = Trade(
        ticker="NFLX",
        direction="BUY",
        entry_time=datetime.now(timezone.utc),
        entry_price=400.0,
        stop_loss=390.0,
        quantity=4,
        take_profit=420.0,
    )
    position = service.open_position(trade=trade, strategy_id="trend", strategy_name="Trend", decision_id="DEC-NFLX")
    service.close_position(position.position_id, exit_price=420.0, reason="TAKE_PROFIT")
    provider = JournalDataProvider(journal_service=service.journal_service, paper_trading_service=service)
    provider.get_trade_journal_data()

    csv_data, csv_name, csv_mime = provider.export(format_name="csv")
    xls_data, xls_name, xls_mime = provider.export(format_name="excel")
    json_data, json_name, json_mime = provider.export(format_name="json")

    assert csv_name.endswith(".csv")
    assert csv_mime == "text/csv"
    assert b"journal_id" in csv_data

    assert xls_name.endswith(".xls")
    assert xls_mime == "application/vnd.ms-excel"
    assert b"Workbook" in xls_data

    assert json_name.endswith(".json")
    assert json_mime == "application/json"
    payload = json.loads(json_data.decode("utf-8"))
    assert isinstance(payload, list)
    assert payload[0]["symbol"] == "NFLX"


def test_notes_persistence_and_snapshot_immutability() -> None:
    service = _build_service()

    trade = Trade(
        ticker="AMD",
        direction="BUY",
        entry_time=datetime.now(timezone.utc),
        entry_price=150.0,
        stop_loss=145.0,
        quantity=10,
        take_profit=170.0,
    )
    position = service.open_position(trade=trade, strategy_id="mean", strategy_name="Mean", decision_id="DEC-AMD")
    service.close_position(position.position_id, exit_price=170.0, reason="TAKE_PROFIT")

    provider = JournalDataProvider(journal_service=service.journal_service, paper_trading_service=service)
    before = provider.get_trade_journal_data()
    entry = before["entries"][0]
    journal_id = entry["journal_id"]
    snapshot_before = json.dumps(entry["decision_snapshot"], sort_keys=True)

    assert provider.save_note(journal_id, "Review setup quality") is True
    after = provider.get_trade_journal_data(selected_journal_id=journal_id)
    selected = after["selected_trade"]

    assert selected["notes"] == "Review setup quality"
    snapshot_after = json.dumps(selected["decision_snapshot"], sort_keys=True)
    assert snapshot_before == snapshot_after
