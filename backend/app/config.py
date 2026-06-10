import json
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.features.workspace.core.constants import EMBEDDING_MODEL_NAME


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

    available_models: list[dict[str, Any]] = Field(
        default_factory=list,
        validation_alias="AVAILABLE_MODELS",
    )

    @field_validator("available_models", mode="before")
    @classmethod
    def _parse_available_models(cls, value: object) -> list[dict[str, Any]]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise TypeError("AVAILABLE_MODELS must be a JSON array")
            return parsed
        raise TypeError("AVAILABLE_MODELS must be a JSON array string")

    enable_debug_chat_completion: bool = False

    enable_rate_limiting: bool = False

    log_full_llm_prompt: bool = True

    log_openai_http_verbose: bool = False

    access_token_secret: str = Field(validation_alias="ACCESS_TOKEN_SECRET")

    mongodb_uri: str | None = Field(default=None, validation_alias="MONGODB_URI")
    mongodb_db_name: str = Field(
        default="getting_interested",
        validation_alias="MONGODB_DB_NAME",
    )

    data_dir: str = Field(default="data/runtime", validation_alias="DATA_DIR")
    static_data_dir: str = Field(
        default="data/static",
        validation_alias="STATIC_DATA_DIR",
    )
    embedding_model_name: str = Field(
        default=EMBEDDING_MODEL_NAME,
        validation_alias="EMBEDDING_MODEL_NAME",
    )
    hf_token: str | None = Field(default=None, validation_alias="HF_TOKEN")

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
