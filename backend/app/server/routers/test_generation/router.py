from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.core.actions.derive_question_metrics import DeriveQuestionMetricsAction
from app.domains.tests.service import TestService
from app.features.generation.llm.v1 import FullTestV1Pipeline
from app.features.generation.llm.v2 import FullTestV2Pipeline
from app.server.client_disconnect import (
    ClientDisconnectedError,
    cancel_on_client_disconnect,
)
from app.server.dependencies.item_analysis import (
    get_optional_item_analysis_action,
    get_test_service,
)
from app.server.dependencies.langchain import ChatModelFactory, bind_chat_model
from app.server.middleware.rate_limiting import limiter
from app.server.routers.test_generation.schemas import (
    GenerateTestRequest,
    GenerateTestResponse,
)

router = APIRouter(prefix="/api")


def _raise_invalid_model(model: str, allowed_ids: set[str]) -> None:
    raise HTTPException(
        status_code=422,
        detail=(
            f"Model '{model}' is not available. Valid models: {sorted(allowed_ids)}"
        ),
    )


@router.post("/generate/test", response_model=GenerateTestResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def generate_test(
    request: Request,
    body: GenerateTestRequest,
    chat_model_factory: ChatModelFactory,
    test_service: Annotated[TestService, Depends(get_test_service)],
    item_analysis_action: Annotated[
        DeriveQuestionMetricsAction | None,
        Depends(get_optional_item_analysis_action),
    ],
) -> GenerateTestResponse:
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
            derive_metrics_action=item_analysis_action,
        )

    llm = bind_chat_model(chat_model_factory, body.model)

    async def _run_generation() -> GenerateTestResponse:
        generated_test, cost_usd = await test_pipeline.run(body.model, llm)
        return GenerateTestResponse.from_generated_test(
            generated_test,
            model_used=body.model,
            cost_usd=cost_usd,
        )

    try:
        return await cancel_on_client_disconnect(request, _run_generation())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")
