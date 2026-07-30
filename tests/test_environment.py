"""
===========================================================
TradePilotAI Operating System
Environment Manager Tests
===========================================================
"""

import os

from tradepilotai_os.core.environment import EnvironmentManager


def test_environment_manager_creation():
    """EnvironmentManager should instantiate."""

    env = EnvironmentManager()

    assert env is not None


def test_get_default_value():
    """Unknown keys should return the supplied default."""

    env = EnvironmentManager()

    assert env.get("THIS_KEY_DOES_NOT_EXIST", "default") == "default"


def test_exists():
    """Existing environment variables should be detected."""

    os.environ["TEST_ENVIRONMENT_KEY"] = "value"

    env = EnvironmentManager()

    assert env.exists("TEST_ENVIRONMENT_KEY")

    del os.environ["TEST_ENVIRONMENT_KEY"]


def test_get_int():
    """Integer values should be converted correctly."""

    os.environ["TEST_INT"] = "42"

    env = EnvironmentManager()

    assert env.get_int("TEST_INT") == 42

    del os.environ["TEST_INT"]


def test_get_bool():
    """Boolean values should be interpreted correctly."""

    os.environ["TEST_BOOL"] = "true"

    env = EnvironmentManager()

    assert env.get_bool("TEST_BOOL") is True

    del os.environ["TEST_BOOL"]