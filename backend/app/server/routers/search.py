from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.features.workspace.course_tests.models import FewShotResult
from app.features.workspace.course_tests.service import FewShotSearchService
from app.server.dependencies.few_shot_search import get_few_shot_search_service

router = APIRouter(prefix="/api")


@router.post("/search/few-shots", response_model=list[FewShotResult])
async def find_few_shots(
    examples: Annotated[list[str], Body(min_length=1)],
    service: Annotated[FewShotSearchService, Depends(get_few_shot_search_service)],
) -> list[FewShotResult]:
    return service.find_few_shots(examples)
