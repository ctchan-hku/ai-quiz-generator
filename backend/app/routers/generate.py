from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.limiter import limiter
from app.models.schemas import MultipleChoiceQuestion, QuizResponse
from app.services.few_shot import normalize_few_shot_examples
from app.services.llm import (
    CHAT_COMPLETION_KWARGS,
    SINGLE_MCQ_MAX_TOKENS,
    FullQuizLlm,
    SingleMcqLlm,
    get_llm_client,
)

router = APIRouter(prefix="/api")


class GenerateQuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=2000)
    num_questions: int = Field(10, ge=0, le=10)
    model: str
    few_shot_examples: list[str] | None = None


class GenerateQuestionRequest(BaseModel):
    model: str
    topic: str = Field(..., min_length=1, max_length=2000)
    question: MultipleChoiceQuestion
    comment: str | None = None

    @field_validator("comment", mode="before")
    @classmethod
    def normalize_comment(cls, v: object) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return v
        s = v.strip()
        if not s:
            return None
        if len(s) > 2000:
            raise ValueError("comment must be at most 2000 characters after trim")
        return s


def _raise_invalid_model(model: str) -> None:
    valid = sorted(settings.available_model_ids)
    raise HTTPException(
        status_code=422,
        detail=f"Model '{model}' is not available. Valid models: {valid}",
    )


@router.post("/generate/quiz", response_model=QuizResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_quiz(
    request: Request,
    body: GenerateQuizRequest,
    client: Annotated[AsyncOpenAI, Depends(get_llm_client)],
) -> QuizResponse:
    if body.model not in settings.available_model_ids:
        _raise_invalid_model(body.model)
    examples = normalize_few_shot_examples(body.few_shot_examples)
    task = FullQuizLlm(
        body.topic,
        body.num_questions,
        few_shot_examples=examples,
    )
    raw, messages = await task.generate(body.model, client)
    chat_completion_kwargs = {"model": body.model, **CHAT_COMPLETION_KWARGS}
    schema = await task.parse_with_retry(
        raw,
        client,
        messages,
        chat_completion_kwargs=chat_completion_kwargs,
    )
    return QuizResponse(questions=schema.questions, model_used=body.model, source="topic")


@router.post("/generate/question", response_model=MultipleChoiceQuestion)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_question(
    request: Request,
    body: GenerateQuestionRequest,
    client: Annotated[AsyncOpenAI, Depends(get_llm_client)],
) -> MultipleChoiceQuestion:
    if body.model not in settings.available_model_ids:
        _raise_invalid_model(body.model)
    task = SingleMcqLlm(body.topic, body.question, body.comment)
    raw, messages = await task.generate(body.model, client)
    chat_completion_kwargs = {
        "model": body.model,
        **CHAT_COMPLETION_KWARGS,
        "max_tokens": SINGLE_MCQ_MAX_TOKENS,
    }
    return await task.parse_with_retry(
        raw,
        client,
        messages,
        chat_completion_kwargs=chat_completion_kwargs,
    )
