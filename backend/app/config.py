import json
from pathlib import Path
from typing import Any

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_AVAILABLE_MODELS: list[dict[str, str]] = [
    {"id": "gemini-3-flash", "label": "Gemini 3 Flash"},
    {"id": "gemini-3.1-pro", "label": "Gemini 3.1 Pro"},
    {"id": "claude-sonnet-4.6", "label": "Claude Sonnet 4.6"},
    {"id": "gpt-5.1-instant", "label": "GPT-5.1 Instant"},
    {"id": "grok-4.20-multi-agent", "label": "Grok 4.20 (multi-agent)"},
    {"id": "deepseek-v4-pro-e", "label": "DeepSeek V4 Pro-E"},
]

OPENAI_BASE_URL_DEFAULT = "https://api.poe.com/v1"
DATA_DIR_DEFAULT = "data/runtime"
STATIC_DATA_DIR_DEFAULT = "data/static"

SECRETS_ENV_FILE_CANDIDATES = (
    Path("/run/secrets/deposit/.env"),
    Path("/run/secrets/.env"),
)


def secrets_env_files() -> tuple[Path, ...]:
    return tuple(path for path in SECRETS_ENV_FILE_CANDIDATES if path.is_file())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=secrets_env_files(),
        env_file_encoding="utf-8",
    )

    # Secrets
    openai_api_key: str
    access_token_secret: str | None = Field(
        default=None,
        validation_alias="ACCESS_TOKEN_SECRET",
    )
    mongodb_uri: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MONGODB_URI", "MONGODB_CONNECTION_STRING"),
    )
    database_name: str | None = Field(
        default=None,
        validation_alias="DATABASE_NAME",
    )
    hf_token: str | None = Field(default=None, validation_alias="HF_TOKEN")

    # OpenAI / LLM
    openai_base_url: str = OPENAI_BASE_URL_DEFAULT
    available_models: list[dict[str, Any]] = Field(
        default_factory=lambda: list(DEFAULT_AVAILABLE_MODELS),
        validation_alias="AVAILABLE_MODELS",
    )

    # Paths
    data_dir: str = Field(default=DATA_DIR_DEFAULT, validation_alias="DATA_DIR")
    static_data_dir: str = Field(
        default=STATIC_DATA_DIR_DEFAULT,
        validation_alias="STATIC_DATA_DIR",
    )

    @field_validator("mongodb_uri", mode="before")
    @classmethod
    def _normalize_mongodb_uri(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("database_name", mode="before")
    @classmethod
    def _normalize_database_name(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def _require_database_name_with_mongodb(self) -> "Settings":
        if self.mongodb_uri and not self.database_name:
            raise ValueError("DATABASE_NAME is required when MONGODB_URI is set")
        return self

    @field_validator("available_models", mode="before")
    @classmethod
    def _parse_available_models(cls, value: Any) -> Any:
        if isinstance(value, str):
            return json.loads(value)
        return value

    @field_validator("access_token_secret", mode="before")
    @classmethod
    def _normalize_secret(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def poe_models_pricing_path(self) -> Path:
        return Path(self.static_data_dir) / "poe_models_pricing.json"


settings = Settings()
