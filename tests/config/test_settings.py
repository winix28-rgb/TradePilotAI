"""
===========================================================
TradePilotAI
Settings Tests
===========================================================
"""

from config.settings import Settings



def test_default_mode(monkeypatch):

    monkeypatch.delenv(
        "TRADEPILOT_MODE",
        raising=False,
    )


    settings = Settings.load()


    assert settings.mode == "BACKTEST"



def test_ig_account_type_default(monkeypatch):

    monkeypatch.delenv(
        "IG_ACCOUNT_TYPE",
        raising=False,
    )


    settings = Settings.load()


    assert settings.ig_account_type == "DEMO"



def test_environment_values(monkeypatch):

    monkeypatch.setenv(
        "TRADEPILOT_MODE",
        "DEMO",
    )


    monkeypatch.setenv(
        "IG_USERNAME",
        "user",
    )


    settings = Settings.load()


    assert settings.mode == "DEMO"

    assert settings.ig_username == "user"