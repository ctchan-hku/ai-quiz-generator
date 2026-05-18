from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.server.client_disconnect import (
    ClientDisconnectedError,
    cancel_on_client_disconnect,
)
from app.integrations.openai.client import OpenAiChat
from app.modules.generation.helpers.cost import calculate_cost
from app.modules.generation.llm.v1 import (
    FullQuizV1Pipeline,
    QuestionPipeline,
)
from app.modules.generation.llm.v2 import FullQuizV2Pipeline
from app.modules.generation.models import (
    GenerateQuestionRequest,
    GenerateQuizRequest,
    QuestionGenerateResponse,
    QuizResponse,
)
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


def _raise_invalid_model(model: str, allowed_ids: set[str]) -> None:
    raise HTTPException(
        status_code=422,
        detail=(
            f"Model '{model}' is not available. "
            f"Valid models: {sorted(allowed_ids)}"
        ),
    )


@router.post("/generate/quiz", response_model=QuizResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_quiz(
    request: Request,
    body: GenerateQuizRequest,
    llm: Annotated[OpenAiChat, Depends(OpenAiChat.create)],
) -> QuizResponse:
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model not in allowed_ids:
        _raise_invalid_model(body.model, allowed_ids)
    if body.pipeline_version == 1:
        quiz_pipeline = FullQuizV1Pipeline(
            topic=body.topic,
            num_questions=body.num_questions,
            few_shot_examples=body.few_shot_examples,
            user_instructions=body.user_instructions,
        )
    else:
        quiz_pipeline = FullQuizV2Pipeline(
            topic=body.topic,
            num_questions=body.num_questions,
            few_shot_examples=body.few_shot_examples,
            user_instructions=body.user_instructions,
        )

    async def _run_generation() -> QuizResponse:
        schema, usage_total = await quiz_pipeline.run(body.model, llm)
        cost = calculate_cost(body.model, usage_total)
        return QuizResponse(
            questions=schema.questions,
            model_used=body.model,
            source="topic",
            cost_usd=cost,
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
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model not in allowed_ids:
        _raise_invalid_model(body.model, allowed_ids)
    question_pipeline = QuestionPipeline(body.topic, body.question, body.comment)

    async def _run_generation() -> QuestionGenerateResponse:
        parsed, usage_total = await question_pipeline.run(body.model, llm)
        cost = calculate_cost(body.model, usage_total)
        return QuestionGenerateResponse(question=parsed, cost_usd=cost)

    try:
        return await cancel_on_client_disconnect(request, _run_generation())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")
