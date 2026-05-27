from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.modules.generation.llm.question_editor.pipeline import QuestionPipeline
from app.server.client_disconnect import (
    ClientDisconnectedError,
    cancel_on_client_disconnect,
)
from app.server.dependencies.langchain import ChatModelFactory, bind_chat_model
from app.server.middleware.rate_limiting import limiter
from app.server.routers.question_edit.schemas import (
    QuestionEditRequest,
    QuestionEditResponse,
)

router = APIRouter(prefix="/api")


def _raise_invalid_model(model: str, allowed_ids: set[str]) -> None:
    raise HTTPException(
        status_code=422,
        detail=(
            f"Model '{model}' is not available. Valid models: {sorted(allowed_ids)}"
        ),
    )


@router.post("/edit/question", response_model=QuestionEditResponse)
@limiter.shared_limit("3/hour", scope="openai_generate_quota")
async def edit_question(
    request: Request,
    body: QuestionEditRequest,
    chat_model_factory: ChatModelFactory,
) -> QuestionEditResponse:
    allowed_ids = {m["id"] for m in settings.available_models}
    if body.model not in allowed_ids:
        _raise_invalid_model(body.model, allowed_ids)
    question_pipeline = QuestionPipeline(body.topic, body.question, body.comment)
    llm = bind_chat_model(chat_model_factory, body.model)

    async def _run_edit() -> QuestionEditResponse:
        question, cost_usd = await question_pipeline.run(body.model, llm)
        return QuestionEditResponse(question=question, cost_usd=cost_usd)

    try:
        return await cancel_on_client_disconnect(request, _run_edit())
    except ClientDisconnectedError:
        raise HTTPException(status_code=499, detail="Client disconnected")
