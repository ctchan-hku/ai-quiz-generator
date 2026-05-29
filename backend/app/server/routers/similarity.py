from typing import Annotated

from fastapi import APIRouter, Depends

from app.features.similarity.models import (
    FewShotSimilarityRequest,
    FewShotSimilarityResponse,
)
from app.features.similarity.service import SimilarityService
from app.server.dependencies.similarity import get_similarity_service

router = APIRouter(prefix="/api")


@router.post("/similarity/few-shot", response_model=FewShotSimilarityResponse)
async def find_similar_few_shot_examples(
    body: FewShotSimilarityRequest,
    service: Annotated[SimilarityService, Depends(get_similarity_service)],
) -> FewShotSimilarityResponse:
    return service.find_similar_for_examples(body.examples)
