from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.server.client_disconnect import (
    ClientDisconnectedError,
    cancel_on_client_disconnect,
)
from app.utils.price_catalog import estimate_usage_cost
from app.integrations.openai.client import OpenAiChat
from app.modules.generation.llm.v1 import FullQuizV1Pipeline, SingleQuestionGenerator
from app.modules.generation.llm.v2 import FullQuizV2Pipeline
from app.modules.generation.models import (
    GenerateQuestionRequest,
    GenerateQuizRequest,
    QuestionGenerateResponse,
    QuizResponse,
)
from app.server.middleware.rate_limiting import limiter

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
    llm: Annotated[OpenAiChat, Depends(OpenAiChat.create)],
) -> QuizResponse:
    if body.model not in settings.available_model_ids:
        _raise_invalid_model(body.model)
    pipeline_kwargs = dict(
        topic=body.topic,
        num_questions=body.num_questions,
        few_shot_examples=body.few_shot_examples,
        user_instructions=body.user_instructions,
    )
    if body.pipeline_version == 1:
        quiz_pipeline = FullQuizV1Pipeline(**pipeline_kwargs)
    else:
        quiz_pipeline = FullQuizV2Pipeline(**pipeline_kwargs)

    async def _run_generation() -> QuizResponse:
        schema, usage_total = await quiz_pipeline.run(body.model, llm)
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

    try:
        return await cancel_on_client_disconnect(request, _run_generation())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")


@router.post("/generate/question", response_model=QuestionGenerateResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_question(
    request: Request,
    body: GenerateQuestionRequest,
    llm: Annotated[OpenAiChat, Depends(OpenAiChat.create)],
) -> QuestionGenerateResponse:
    if body.model not in settings.available_model_ids:
        _raise_invalid_model(body.model)
    question_generator = SingleQuestionGenerator(
        body.topic, body.question, body.comment
    )

    async def _run_generation() -> QuestionGenerateResponse:
        raw, messages, usage_first = await question_generator.generate(
            body.model, llm
        )
        parsed, usage_total = await question_generator.parse_with_retry(
            raw,
            llm,
            messages,
            model=body.model,
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

    try:
        return await cancel_on_client_disconnect(request, _run_generation())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")
