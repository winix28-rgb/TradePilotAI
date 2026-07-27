"""
===========================================================
TradePilotAI
Position Sizing Integration Tests
===========================================================
"""

from models.risk_config import RiskConfig
from portfolio.position_sizer import PositionSizer


def test_position_sizer_calculates_risk_based_quantity():

    portfolio_value = 100000

    config = RiskConfig(
        risk_per_trade=1.0
    )


    position_sizer = PositionSizer(

        account_size=portfolio_value,

        risk_per_trade=(
            config.risk_per_trade
            /
            100
        ),
    )


    quantity = position_sizer.calculate_position_size(

        entry_price=100,

        stop_price=95,
    )


    # £100,000 portfolio
    # 1% risk = £1,000
    # £5 risk per share
    #
    # £1,000 / £5 = 200 shares

    assert quantity == 200



def test_position_value_is_calculated_correctly():

    position_sizer = PositionSizer(

        account_size=100000,

        risk_per_trade=0.01,
    )


    value = position_sizer.position_value(

        shares=200,

        entry_price=100,
    )


    assert value == 20000