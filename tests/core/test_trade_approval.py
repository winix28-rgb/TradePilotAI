"""
===========================================================
TradePilotAI
Trade Approval Tests
===========================================================
"""

from core.trade_approval import TradeApproval
from core.approval_manager import ApprovalManager



def test_trade_starts_pending():

    trade = TradeApproval(
        symbol="RR.L",
        action="BUY",
        quantity=10,
        entry_price=8.50,
    )

    assert trade.is_pending



def test_trade_can_be_approved():

    trade = TradeApproval(
        symbol="RR.L",
        action="BUY",
        quantity=10,
        entry_price=8.50,
    )


    trade.approve()


    assert trade.is_approved



def test_manager_approves_trade():

    manager = ApprovalManager()


    trade = TradeApproval(
        symbol="RR.L",
        action="BUY",
        quantity=10,
        entry_price=8.50,
    )


    manager.add(trade)


    result = manager.approve(
        "RR.L"
    )


    assert result.status == "APPROVED"