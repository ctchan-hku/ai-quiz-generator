from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.features.similarity.models import SimilarityResult
from app.features.similarity.service import SimilarityService
from app.server.dependencies.similarity import get_similarity_service

router = APIRouter(prefix="/api")


@router.post("/similarity/few-shot", response_model=list[SimilarityResult])
async def find_similar_few_shot_examples(
    examples: Annotated[list[str], Body(min_length=1)],
    service: Annotated[SimilarityService, Depends(get_similarity_service)],
) -> list[SimilarityResult]:
    return service.find_similar_for_examples(examples)
