"""
===========================================================
TradePilotAI
Trade Journal Tests
===========================================================
"""

from core.trade_journal import TradeJournal



def test_journal_records_event():

    journal = TradeJournal()


    journal.record(

        "SIGNAL",

        "RR.L",

        {
            "action": "BUY"
        }

    )


    assert journal.count() == 1



def test_journal_returns_events():

    journal = TradeJournal()


    journal.record(
        "APPROVED",
        "RR.L"
    )


    events = journal.events()


    assert events[0]["type"] == "APPROVED"



def test_multiple_events():

    journal = TradeJournal()


    journal.record(
        "SIGNAL",
        "RR.L"
    )


    journal.record(
        "EXECUTED",
        "RR.L"
    )


    assert journal.count() == 2