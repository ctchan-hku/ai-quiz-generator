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


def test_mongodb_connection_string_from_env(
    base_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb://gear-host:27017")
    monkeypatch.setenv("DATABASE_NAME", "getting_interested")

    settings = Settings()

    assert settings.mongodb_connection_string == "mongodb://gear-host:27017"
    assert settings.database_name == "getting_interested"


def test_database_name_required_when_mongodb_connection_string_set(
    base_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")

    with pytest.raises(ValueError, match="DATABASE_NAME is required"):
        Settings()


def test_settings_loads_env_file_without_shell_interpretation(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=`literal-backtick-key`\n")

    settings = Settings(_env_file=env_file)

    assert settings.openai_api_key == "`literal-backtick-key`"
