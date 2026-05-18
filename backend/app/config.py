import json
import logging
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Serialized into AVAILABLE_MODELS Field default when env omits the variable.
_FALLBACK_AVAILABLE_MODELS: list[dict[str, Any]] = []


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_base_url: str = "https://api.openai-hk.com/v1"

    #: Seconds for each OpenAI-compatible HTTP request (chat completions).
    openai_http_timeout_seconds: float = Field(
        120.0,
        validation_alias="OPENAI_HTTP_TIMEOUT",
        ge=10.0,
        le=1800.0,
    )

    #: Optional longer read/pool/write timeout (e.g. v2 answer step, slow models).
    #: Defaults to ``OPENAI_HTTP_TIMEOUT`` when omitted.
    openai_http_read_timeout_seconds: float | None = Field(
        None,
        validation_alias="OPENAI_HTTP_READ_TIMEOUT",
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
        """Parse AVAILABLE_MODELS as a JSON array of model objects."""

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
