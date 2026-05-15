from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings
from app.helpers.openai_timeout import openai_httpx_timeout

router = APIRouter(prefix="/api/debug")

MAX_DEBUG_COMPLETION_TOKENS = 64
DEBUG_COMPLETION_TEMPERATURE = 0.7
DEFAULT_DEBUG_MESSAGE = "Say hello in exactly three words."


class DebugChatRequest(BaseModel):
    model: str = Field(
        description="Model id; must be listed in AVAILABLE_MODELS (D-09).",
    )
    message: str = Field(
        default=DEFAULT_DEBUG_MESSAGE,
        description="Short user message; kept small for a smoke test.",
    )


@router.post("/chat-completion")
async def debug_chat_completion(body: DebugChatRequest) -> dict[str, str]:
    """Gated LLM smoke test. Mounted only when ENABLE_DEBUG_CHAT_COMPLETION=true (D-08, D-10)."""
    if body.model in settings.available_model_ids:
        client = AsyncOpenAI(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
            timeout=openai_httpx_timeout(),
        )
        try:
            response = await client.chat.completions.create(
                model=body.model,
                messages=[{"role": "user", "content": body.message}],
                max_tokens=MAX_DEBUG_COMPLETION_TOKENS,
                temperature=DEBUG_COMPLETION_TEMPERATURE,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"LLM call failed: {exc}",
            ) from exc

        reply = response.choices[0].message.content or ""
        return {"reply": reply, "model_used": body.model}

    raise HTTPException(
        status_code=400,
        detail=(
            f"Model '{body.model}' is not in the AVAILABLE_MODELS allowlist. "
            f"Allowed: {sorted(settings.available_model_ids)}"
        ),
    )
