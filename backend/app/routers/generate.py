from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings
from app.limiter import limiter
from app.models.schemas import QuizResponse
from app.services.few_shot import normalize_few_shot_examples
from app.services.llm import CHAT_COMPLETION_KWARGS, generate_quiz, get_llm_client
from app.services.parser import parse_with_retry

router = APIRouter(prefix="/api")


class GenerateTextRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=2000)
    num_questions: int = Field(10, ge=0, le=10)
    model: str
    few_shot_examples: list[str] | None = None


@router.post("/generate/text", response_model=QuizResponse)
@limiter.limit("3/hour")
async def generate_text(
    request: Request,
    body: GenerateTextRequest,
    client: Annotated[AsyncOpenAI, Depends(get_llm_client)],
) -> QuizResponse:
    if body.model not in settings.available_model_ids:
        valid = sorted(settings.available_model_ids)
        raise HTTPException(
            status_code=422,
            detail=f"Model '{body.model}' is not available. Valid models: {valid}",
        )
    examples = normalize_few_shot_examples(body.few_shot_examples)
    raw, messages = await generate_quiz(
        body.topic,
        body.num_questions,
        body.model,
        client,
        few_shot_examples=examples,
    )
    chat_completion_kwargs = {"model": body.model, **CHAT_COMPLETION_KWARGS}
    schema = await parse_with_retry(
        raw,
        client,
        messages,
        chat_completion_kwargs=chat_completion_kwargs,
    )
    return QuizResponse(questions=schema.questions, model_used=body.model, source="topic")
