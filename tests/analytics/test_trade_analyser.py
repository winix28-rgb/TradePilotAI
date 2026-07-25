"""
===========================================================
TradePilotAI
Trade Analyser Tests
===========================================================
"""

from datetime import datetime, timedelta

from analytics.trade_analyser import TradeAnalyser
from models.trade import Trade


def create_trade(
    entry_price,
    exit_price,
    days=1,
):
    """
    Create a test trade.
    """

    start = datetime.now()
    end = start + timedelta(days=days)

    return Trade(
        symbol="RR.L",
        quantity=100,
        entry_price=entry_price,
        exit_price=exit_price,
        entry_date=start,
        exit_date=end,
    )


def test_empty_trade_list():

    analyser = TradeAnalyser([])

    assert analyser.total_trades == 0
    assert analyser.winning_trades == 0
    assert analyser.losing_trades == 0
    assert analyser.net_profit == 0.0
    assert analyser.win_rate == 0.0
    assert analyser.expectancy == 0.0
    assert analyser.profit_factor == 0.0
    assert analyser.average_duration == timedelta(0)


def test_single_winning_trade():

    analyser = TradeAnalyser([
        create_trade(100, 110)
    ])

    assert analyser.total_trades == 1
    assert analyser.winning_trades == 1
    assert analyser.losing_trades == 0
    assert analyser.realised_profit == 1000
    assert analyser.net_profit == 1000
    assert analyser.win_rate == 100.0


def test_single_losing_trade():

    analyser = TradeAnalyser([
        create_trade(100, 90)
    ])

    assert analyser.total_trades == 1
    assert analyser.winning_trades == 0
    assert analyser.losing_trades == 1
    assert analyser.realised_loss == -1000
    assert analyser.net_profit == -1000
    assert analyser.win_rate == 0.0


def test_mixed_trades():

    analyser = TradeAnalyser([
        create_trade(100, 110),
        create_trade(100, 90),
        create_trade(100, 120),
    ])

    assert analyser.total_trades == 3
    assert analyser.winning_trades == 2
    assert analyser.losing_trades == 1

    assert analyser.realised_profit == 3000
    assert analyser.realised_loss == -1000
    assert analyser.net_profit == 2000

    assert analyser.largest_winner == 2000
    assert analyser.largest_loser == -1000

    assert round(analyser.win_rate, 2) == 66.67


def test_average_duration():

    analyser = TradeAnalyser([
        create_trade(100, 110, 2),
        create_trade(100, 120, 4),
    ])

    assert analyser.average_duration.days == 3
    assert analyser.longest_duration.days == 4
    assert analyser.shortest_duration.days == 2


def test_len():

    analyser = TradeAnalyser([
        create_trade(100, 110),
        create_trade(100, 120),
    ])

    assert len(analyser) == 2


def test_bool():

    assert not TradeAnalyser([])
    assert TradeAnalyser([
        create_trade(100, 110)
    ])