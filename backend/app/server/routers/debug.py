from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.integrations.openai.client import (
    DEBUG_COMPLETION_TEMPERATURE,
    MAX_DEBUG_COMPLETION_TOKENS,
    CompletionParams,
    OpenAiChat,
)

router = APIRouter(prefix="/api/debug")


class DebugChatRequest(BaseModel):
    model: str = Field(
        description="Model id; must be listed in AVAILABLE_MODELS (D-09).",
    )
    message: str = Field(
        description="User message for the smoke test.",
    )


@router.post("/chat-completion")
async def debug_chat_completion(
    body: DebugChatRequest,
    llm: Annotated[OpenAiChat, Depends(OpenAiChat.create)],
) -> dict[str, str]:
    """Gated LLM smoke test. Mounted only when ENABLE_DEBUG_CHAT_COMPLETION=true (D-08, D-10)."""
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model in allowed_ids:
        try:
            outcome = await llm.complete(
                body.model,
                [{"role": "user", "content": body.message}],
                CompletionParams.plain(
                    max_tokens=MAX_DEBUG_COMPLETION_TOKENS,
                    temperature=DEBUG_COMPLETION_TEMPERATURE,
                ),
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"LLM call failed: {exc}",
            ) from exc

        return {"reply": outcome.text, "model_used": body.model}

    raise HTTPException(
        status_code=400,
        detail=(
            f"Model '{body.model}' is not in the AVAILABLE_MODELS allowlist. "
            f"Allowed: {sorted(allowed_ids)}"
        ),
    )
