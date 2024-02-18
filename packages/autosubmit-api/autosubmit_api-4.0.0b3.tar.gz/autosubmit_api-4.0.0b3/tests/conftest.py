# Conftest file for sharing fixtures 
# Reference: https://docs.pytest.org/en/latest/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files

import os
from flask import Flask
import pytest
from autosubmitconfigparser.config.basicconfig import BasicConfig
from autosubmit_api.app import create_app
from autosubmit_api.config.basicConfig import APIBasicConfig
from tests.custom_utils import custom_return_value

FAKE_EXP_DIR = "./tests/experiments/"


#### FIXTURES ####
@pytest.fixture(autouse=True)
def fixture_disable_protection(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PROTECTION_LEVEL", "NONE")

@pytest.fixture
def fixture_mock_basic_config(monkeypatch: pytest.MonkeyPatch):
    # Patch APIBasicConfig parent BasicConfig
    monkeypatch.setattr(BasicConfig, "read", custom_return_value(None))
    monkeypatch.setattr(APIBasicConfig, "read", custom_return_value(None))
    monkeypatch.setattr(BasicConfig, "LOCAL_ROOT_DIR", FAKE_EXP_DIR)
    monkeypatch.setattr(BasicConfig, "DB_DIR", FAKE_EXP_DIR)
    monkeypatch.setattr(BasicConfig, "DB_FILE", "autosubmit.db")
    monkeypatch.setattr(
        BasicConfig, "DB_PATH", os.path.join(FAKE_EXP_DIR, "autosubmit.db")
    )
    monkeypatch.setattr(BasicConfig, "AS_TIMES_DB", "as_times.db")
    yield APIBasicConfig


@pytest.fixture
def fixture_app(fixture_mock_basic_config):
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def fixture_client(fixture_app: Flask):
    return fixture_app.test_client()


@pytest.fixture
def fixture_runner(fixture_app: Flask):
    return fixture_app.test_cli_runner()
