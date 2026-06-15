import json

import pytest

from app.config import (
    DEFAULT_AVAILABLE_MODELS,
    Settings,
)


@pytest.fixture
def base_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def test_available_models_default(base_env: None) -> None:
    settings = Settings()

    assert settings.available_models == DEFAULT_AVAILABLE_MODELS


def test_available_models_env_override(
    base_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    override = [{"id": "custom-model", "label": "Custom"}]
    monkeypatch.setenv("AVAILABLE_MODELS", json.dumps(override))

    settings = Settings()

    assert settings.available_models == override


def test_mongodb_uri_accepts_gear_connection_string(
    base_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb://gear-host:27017")

    settings = Settings()

    assert settings.mongodb_uri == "mongodb://gear-host:27017"
