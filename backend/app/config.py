import json
import logging
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_FALLBACK_MODELS: list[dict[str, str]] = [
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini (fast)"},
    {"id": "gpt-4o", "label": "GPT-4o (smart)"},
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM proxy — required; startup fails with a clear error if absent
    openai_api_key: str
    openai_base_url: str = "https://api.openai-hk.com/v1"

    # CORS — Phase 1: ALLOWED_ORIGINS=* (D-06); Phase 3: tighten to Vercel + localhost (D-07)
    allowed_origins_raw: str = Field("*", validation_alias="ALLOWED_ORIGINS")

    # Model list as JSON array env var (D-03)
    available_models_raw: str = Field(
        json.dumps(_FALLBACK_MODELS),
        validation_alias="AVAILABLE_MODELS",
    )

    # Debug route gate — defaults to False; MUST remain False on production (D-08, D-10)
    enable_debug_chat_completion: bool = False

    @property
    def allowed_origins(self) -> list[str]:
        """Return list of allowed CORS origins from the ALLOWED_ORIGINS env var.

        Returns ["*"] when the raw value is the literal string "*".
        Splits on commas for multi-origin Phase 3 config (D-07).
        """
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @property
    def available_models(self) -> list[dict[str, Any]]:
        """Parse AVAILABLE_MODELS JSON array. Falls back to hardcoded list on parse error."""
        try:
            parsed = json.loads(self.available_models_raw)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("AVAILABLE_MODELS is not valid JSON; using fallback model list")
        return _FALLBACK_MODELS

    @property
    def available_model_ids(self) -> set[str]:
        """Set of allowlisted model ID strings for debug route validation (D-09)."""
        return {m["id"] for m in self.available_models}


settings = Settings()
