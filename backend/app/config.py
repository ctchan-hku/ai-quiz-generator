import json
from pathlib import Path
from typing import Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.features.workspace.core.constants import EMBEDDING_MODEL_NAME

# --- Defaults (single source of truth for fallbacks) ---

DEFAULT_AVAILABLE_MODELS: list[dict[str, str]] = [
    {"id": "gemini-3-flash", "label": "Gemini 3 Flash"},
    {"id": "gemini-3.1-pro", "label": "Gemini 3.1 Pro"},
    {"id": "claude-sonnet-4.6", "label": "Claude Sonnet 4.6"},
    {"id": "gpt-5.1-instant", "label": "GPT-5.1 Instant"},
    {"id": "grok-4.20-multi-agent", "label": "Grok 4.20 (multi-agent)"},
    {"id": "deepseek-v4-pro-e", "label": "DeepSeek V4 Pro-E"},
]

OPENAI_BASE_URL_DEFAULT = "https://api.poe.com/v1"
MONGODB_DB_NAME_DEFAULT = "getting_interested"
DATA_DIR_DEFAULT = "data/runtime"
STATIC_DATA_DIR_DEFAULT = "data/static"
ALLOWED_ORIGINS_DEFAULT = "*"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

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
    hf_token: str | None = Field(default=None, validation_alias="HF_TOKEN")

    # MongoDB
    mongodb_db_name: str = Field(
        default=MONGODB_DB_NAME_DEFAULT,
        validation_alias="MONGODB_DB_NAME",
    )

    # OpenAI / LLM
    openai_base_url: str = OPENAI_BASE_URL_DEFAULT
    available_models: list[dict[str, Any]] = Field(
        default_factory=lambda: list(DEFAULT_AVAILABLE_MODELS),
        validation_alias="AVAILABLE_MODELS",
    )
    openai_http_timeout_seconds: float = Field(
        120.0,
        ge=10.0,
        le=1800.0,
    )
    openai_http_read_timeout_seconds: float | None = Field(
        None,
        ge=10.0,
        le=1800.0,
    )

    # CORS
    allowed_origins_raw: str = Field(
        ALLOWED_ORIGINS_DEFAULT,
        validation_alias="ALLOWED_ORIGINS",
    )

    # Feature flags
    enable_debug_chat_completion: bool = False
    enable_rate_limiting: bool = False
    log_full_llm_prompt: bool = False
    log_openai_http_verbose: bool = False

    # Paths
    data_dir: str = Field(default=DATA_DIR_DEFAULT, validation_alias="DATA_DIR")
    static_data_dir: str = Field(
        default=STATIC_DATA_DIR_DEFAULT,
        validation_alias="STATIC_DATA_DIR",
    )
    embedding_model_name: str = Field(
        default=EMBEDDING_MODEL_NAME,
        validation_alias="EMBEDDING_MODEL_NAME",
    )

    @field_validator("mongodb_uri", mode="before")
    @classmethod
    def _normalize_mongodb_uri(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value

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

    @property
    def allowed_origins(self) -> list[str]:
        """Split ``ALLOWED_ORIGINS`` on commas, or ``["*"]`` when the value is ``*``."""
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [
            origin.strip()
            for origin in self.allowed_origins_raw.split(",")
            if origin.strip()
        ]


settings = Settings()
