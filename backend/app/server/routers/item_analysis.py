from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.actions.derive_question_metrics import DeriveQuestionMetricsAction
from app.core.domain import ResponseRecord
from app.modules.data.responses.service import ResponseService
from app.modules.item_analysis.models import ItemAnalysisReport
from app.server.dependencies.item_analysis import (
    get_item_analysis_action,
    get_response_service,
)

router = APIRouter(prefix="/api")


@router.get("/tests/{test_id}/responses", response_model=list[ResponseRecord])
async def list_test_responses(
    test_id: str,
    service: Annotated[ResponseService, Depends(get_response_service)],
) -> list[ResponseRecord]:
    """Return responses for a test where template.id matches and template.type is test."""
    return await service.list_by_test_id(test_id)


@router.get(
    "/tests/{test_id}/question-metrics",
    response_model=ItemAnalysisReport,
)
async def get_test_item_analysis(
    test_id: str,
    action: Annotated[DeriveQuestionMetricsAction, Depends(get_item_analysis_action)],
) -> ItemAnalysisReport:
    """Return option selection rates, difficulty index, and discrimination index per scored question (item analysis)."""
    results = await action.execute([test_id])
    return results[0].report if results else ItemAnalysisReport()
