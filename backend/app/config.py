import json
import logging
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.helpers.price_catalog import normalize_model_entry

logger = logging.getLogger(__name__)

# Serialized into AVAILABLE_MODELS Field default when env omits the variable.
_FALLBACK_AVAILABLE_MODELS: list[dict[str, Any]] = []


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_base_url: str = "https://api.openai-hk.com/v1"

    allowed_origins_raw: str = Field("*", validation_alias="ALLOWED_ORIGINS")

    available_models_raw: str = Field(
        json.dumps(_FALLBACK_AVAILABLE_MODELS),
        validation_alias="AVAILABLE_MODELS",
    )

    enable_debug_chat_completion: bool = False

    enable_rate_limiting: bool = False

    log_full_llm_prompt: bool = Field(True, validation_alias="LOG_FULL_LLM_PROMPT")

    #: When true, sets ``openai._base_client`` to DEBUG so retry reasons (HTTP status,
    #: timeouts, connection errors) appear above ``Retrying request to …`` lines.
    log_openai_http_verbose: bool = Field(
        False,
        validation_alias="LOG_OPENAI_HTTP_VERBOSE",
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Return list of allowed CORS origins from the ALLOWED_ORIGINS env var.

        Returns ["*"] when the raw value is the literal string "*".
        Splits on commas for multi-origin Phase 3 config (D-07).
        """
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [
            origin.strip()
            for origin in self.allowed_origins_raw.split(",")
            if origin.strip()
        ]

    @property
    def available_models(self) -> list[dict[str, Any]]:
        """Parse AVAILABLE_MODELS JSON array; normalize each allowlisted model entry."""
        try:
            env_model_entries = json.loads(self.available_models_raw)
            return [normalize_model_entry(dict(x)) for x in env_model_entries]
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning(
                "AVAILABLE_MODELS is not valid JSON; using fallback model list",
            )
            return [normalize_model_entry(dict(x)) for x in _FALLBACK_AVAILABLE_MODELS]

    @property
    def available_model_ids(self) -> set[str]:
        """Set of allowlisted model ID strings for debug route validation (D-09)."""
        return {m["id"] for m in self.available_models}


settings = Settings()
