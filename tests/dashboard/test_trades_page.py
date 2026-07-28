"""
===========================================================
TradePilotAI
Trade History Tests
===========================================================
"""

from core.trade_journal import TradeJournal



def test_trade_history_records():

    journal = TradeJournal()


    journal.record(
        "SIGNAL",
        "RR.L",
        {
            "action": "BUY"
        }
    )


    events = journal.events()


    assert len(events) == 1

    assert events[0]["symbol"] == "RR.L"

    assert events[0]["type"] == "SIGNAL"