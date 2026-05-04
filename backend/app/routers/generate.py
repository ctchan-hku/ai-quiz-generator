from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI

from app.config import settings
from app.limiter import limiter
from app.helpers.model_catalog import estimate_usage_cost
from app.models.generate_requests import GenerateQuestionRequest, GenerateQuizRequest
from app.models.generate_responses import QuestionGenerateResponse, QuizResponse
from app.services.prompt_sections.few_shot import FEW_SHOT_FORMATTER
from app.services.prompt_sections.user_instructions import USER_INSTRUCTIONS_FORMATTER
from app.services.llm import (
    CHAT_COMPLETION_KWARGS,
    SINGLE_MCQ_MAX_TOKENS,
    FullQuizLlm,
    SingleMcqLlm,
    get_llm_client,
)

router = APIRouter(prefix="/api")


def _models_catalog(request: Request) -> list[dict[str, Any]]:
    """Same merged catalog as GET /api/models when present; else env-available_models."""

    merged = getattr(request.app.state, "models_catalog", None)
    if isinstance(merged, list) and merged:
        return merged
    return list(settings.available_models)


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
    few_shot = FEW_SHOT_FORMATTER.normalize(body.few_shot_examples)
    user_instr = USER_INSTRUCTIONS_FORMATTER.normalize(body.user_instructions)
    task = FullQuizLlm(
        body.topic,
        body.num_questions,
        few_shot_examples=few_shot,
        user_instructions=user_instr,
    )
    raw, messages, usage_first = await task.generate(body.model, client)
    chat_completion_kwargs = {"model": body.model, **CHAT_COMPLETION_KWARGS}
    schema, usage_total = await task.parse_with_retry(
        raw,
        client,
        messages,
        chat_completion_kwargs=chat_completion_kwargs,
        initial_usage=usage_first,
    )
    cost_usd = estimate_usage_cost(
        body.model,
        usage_total.prompt_tokens,
        usage_total.completion_tokens,
        _models_catalog(request),
        log_route="generate_quiz",
    )
    return QuizResponse(
        questions=schema.questions,
        model_used=body.model,
        source="topic",
        cost_usd=cost_usd,
    )


@router.post("/generate/question", response_model=QuestionGenerateResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_question(
    request: Request,
    body: GenerateQuestionRequest,
    client: Annotated[AsyncOpenAI, Depends(get_llm_client)],
) -> QuestionGenerateResponse:
    if body.model not in settings.available_model_ids:
        _raise_invalid_model(body.model)
    task = SingleMcqLlm(body.topic, body.question, body.comment)
    raw, messages, usage_first = await task.generate(body.model, client)
    chat_completion_kwargs = {
        "model": body.model,
        **CHAT_COMPLETION_KWARGS,
        "max_tokens": SINGLE_MCQ_MAX_TOKENS,
    }
    parsed, usage_total = await task.parse_with_retry(
        raw,
        client,
        messages,
        chat_completion_kwargs=chat_completion_kwargs,
        initial_usage=usage_first,
    )
    cost_usd = estimate_usage_cost(
        body.model,
        usage_total.prompt_tokens,
        usage_total.completion_tokens,
        _models_catalog(request),
        log_route="generate_question",
    )
    return QuestionGenerateResponse(question=parsed, cost_usd=cost_usd)
