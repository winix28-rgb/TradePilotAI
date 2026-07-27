"""
===========================================================
TradePilotAI
IG Configuration Tests
===========================================================
"""

import pytest

from config.ig_config import IGConfig



def test_valid_ig_config():

    config = IGConfig(

        username="user",

        password="pass",

        api_key="key",

    )

    assert config.account_type == "DEMO"



def test_empty_username_fails():

    with pytest.raises(ValueError):

        IGConfig(

            username="",

            password="pass",

            api_key="key",

        )



def test_empty_password_fails():

    with pytest.raises(ValueError):

        IGConfig(

            username="user",

            password="",

            api_key="key",

        )



def test_empty_api_key_fails():

    with pytest.raises(ValueError):

        IGConfig(

            username="user",

            password="pass",

            api_key="",

        )