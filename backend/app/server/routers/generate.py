from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.integrations.openai.client import OpenAiChat
from app.modules.data.student_stats.handlers.question_metrics_handler import (
    QuestionMetricsHandler,
)
from app.modules.data.student_stats.services.test_service import TestService
from app.modules.generation.llm.v1 import (
    FullTestV1Pipeline,
    QuestionPipeline,
)
from app.modules.generation.llm.v2 import FullTestV2Pipeline
from app.modules.generation.models import (
    GenerateQuestionRequest,
    GenerateTestRequest,
    QuestionResponse,
    TestResponse,
)
from app.server.client_disconnect import (
    ClientDisconnectedError,
    cancel_on_client_disconnect,
)
from app.server.dependencies.student_stats import (
    get_optional_question_metrics_handler,
    get_test_service,
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


@router.post("/generate/test", response_model=TestResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_test(
    request: Request,
    body: GenerateTestRequest,
    llm: Annotated[OpenAiChat, Depends(OpenAiChat.create)],
    test_service: Annotated[TestService, Depends(get_test_service)],
    question_metrics_handler: Annotated[
        QuestionMetricsHandler | None,
        Depends(get_optional_question_metrics_handler),
    ],
) -> TestResponse:
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model not in allowed_ids:
        _raise_invalid_model(body.model, allowed_ids)
    if body.pipeline_version == 1:
        test_pipeline = FullTestV1Pipeline(
            topic=body.topic,
            num_questions=body.num_questions,
            few_shot_examples=body.few_shot_examples,
            user_instructions=body.user_instructions,
        )
    else:
        await test_service.log_test_names(body.selected_test_ids)
        test_pipeline = FullTestV2Pipeline(
            topic=body.topic,
            num_questions=body.num_questions,
            few_shot_examples=body.few_shot_examples,
            user_instructions=body.user_instructions,
            selected_test_ids=body.selected_test_ids,
            question_metrics_handler=question_metrics_handler,
        )

    async def _run_generation() -> TestResponse:
        schema, cost_usd = await test_pipeline.run(body.model, llm)
        return TestResponse(
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
