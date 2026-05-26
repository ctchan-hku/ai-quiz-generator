from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from app.config import settings
from app.integrations.langchain.config import (
    DEBUG_COMPLETION_TEMPERATURE,
    MAX_DEBUG_COMPLETION_TOKENS,
)
from app.server.dependencies.langchain import ChatModelFactory, bind_chat_model

router = APIRouter(prefix="/api/debug")


class DebugChatRequest(BaseModel):
    model: str = Field(
        description="Model id; must be listed in AVAILABLE_MODELS (D-09).",
    )
    message: str = Field(
        description="User message for the smoke test.",
    )


def _reply_text(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return str(content)


@router.post("/chat-completion")
async def debug_chat_completion(
    body: DebugChatRequest,
    chat_model_factory: ChatModelFactory,
) -> dict[str, str]:
    """Gated LLM smoke test. Mounted only when ENABLE_DEBUG_CHAT_COMPLETION=true (D-08, D-10)."""
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model in allowed_ids:
        llm = bind_chat_model(chat_model_factory, body.model).bind(
            max_tokens=MAX_DEBUG_COMPLETION_TOKENS,
            temperature=DEBUG_COMPLETION_TEMPERATURE,
        )
        try:
            response = await llm.ainvoke([{"role": "user", "content": body.message}])
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"LLM call failed: {exc}",
            ) from exc

        if not isinstance(response, AIMessage):
            raise HTTPException(status_code=503, detail="LLM call returned no message")

        return {"reply": _reply_text(response), "model_used": body.model}

    raise HTTPException(
        status_code=400,
        detail=(
            f"Model '{body.model}' is not in the AVAILABLE_MODELS allowlist. "
            f"Allowed: {sorted(allowed_ids)}"
        ),
    )
