import json
import logging
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_FALLBACK_AVAILABLE_MODELS: list[dict[str, Any]] = []


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_base_url: str = "https://api.openai-hk.com/v1"

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

    allowed_origins_raw: str = Field("*", validation_alias="ALLOWED_ORIGINS")

    available_models_raw: str = Field(
        json.dumps(_FALLBACK_AVAILABLE_MODELS),
        validation_alias="AVAILABLE_MODELS",
    )

    enable_debug_chat_completion: bool = False

    enable_rate_limiting: bool = False

    log_full_llm_prompt: bool = True

    log_openai_http_verbose: bool = False

    mongodb_uri: str | None = Field(
        default=None,
        validation_alias="MONGODB_URI",
    )
    mongodb_db_name: str = Field(
        default="gear_production",
        validation_alias="MONGODB_DB_NAME",
    )

    @field_validator("mongodb_uri", mode="before")
    @classmethod
    def _normalize_mongodb_uri(cls, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        if not isinstance(value, str):
            raise TypeError("MONGODB_URI must be a string when set")
        return value

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

    @property
    def available_models(self) -> list[dict[str, Any]]:
        """``AVAILABLE_MODELS`` must be a JSON array; bad JSON falls back to an empty list."""
        try:
            parsed = json.loads(self.available_models_raw)
            if not isinstance(parsed, list):
                raise TypeError
            return parsed
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "AVAILABLE_MODELS is not valid JSON array; using fallback model list",
            )
            return list(_FALLBACK_AVAILABLE_MODELS)


settings = Settings()
