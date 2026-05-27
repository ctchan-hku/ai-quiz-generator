from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.data.responses.models import ResponseListResponse
from app.modules.data.responses.service import ResponseService
from app.modules.student_stats.handler import QuestionMetricsHandler
from app.modules.student_stats.models import QuestionMetricsResponse
from app.server.dependencies.student_stats import (
    get_question_metrics_handler,
    get_response_service,
)

router = APIRouter(prefix="/api")


@router.get("/tests/{test_id}/responses", response_model=ResponseListResponse)
async def list_test_responses(
    test_id: str,
    service: Annotated[ResponseService, Depends(get_response_service)],
) -> ResponseListResponse:
    """Return responses for a test where template.id matches and template.type is test."""
    return await service.list_by_test_id(test_id)


@router.get(
    "/tests/{test_id}/question-metrics",
    response_model=QuestionMetricsResponse,
)
async def get_test_question_metrics(
    test_id: str,
    handler: Annotated[QuestionMetricsHandler, Depends(get_question_metrics_handler)],
) -> QuestionMetricsResponse:
    """Return option selection rates, difficulty index, and discrimination index per scored question."""
    return await handler.get_by_test_id(test_id)
