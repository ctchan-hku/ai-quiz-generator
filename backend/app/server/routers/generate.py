from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.integrations.openai.client import OpenAiChat
from app.modules.generation.llm.v1 import (
    FullQuizV1Pipeline,
    QuestionPipeline,
)
from app.modules.generation.llm.v2 import FullQuizV2Pipeline
from app.modules.generation.models import (
    GenerateQuestionRequest,
    GenerateQuizRequest,
    QuestionResponse,
    QuizResponse,
)
from app.server.client_disconnect import (
    ClientDisconnectedError,
    cancel_on_client_disconnect,
)
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


def _raise_invalid_model(model: str, allowed_ids: set[str]) -> None:
    raise HTTPException(
        status_code=422,
        detail=(
            f"Model '{model}' is not available. Valid models: {sorted(allowed_ids)}"
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
        schema, cost_usd = await quiz_pipeline.run(body.model, llm)
        return QuizResponse(
            questions=schema.questions,
            model_used=body.model,
            cost_usd=cost_usd,
        )

    try:
        return await cancel_on_client_disconnect(request, _run_generation())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")


@router.post("/generate/question", response_model=QuestionResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_question(
    request: Request,
    body: GenerateQuestionRequest,
    llm: Annotated[OpenAiChat, Depends(OpenAiChat.create)],
) -> QuestionResponse:
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model not in allowed_ids:
        _raise_invalid_model(body.model, allowed_ids)
    question_pipeline = QuestionPipeline(body.topic, body.question, body.comment)

    async def _run_generation() -> QuestionResponse:
        parsed, cost_usd = await question_pipeline.run(body.model, llm)
        return QuestionResponse(question=parsed, cost_usd=cost_usd)

    try:
        return await cancel_on_client_disconnect(request, _run_generation())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")
