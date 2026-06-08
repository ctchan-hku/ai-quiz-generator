from app.features.workspace.course_tests.constants import SEARCH_TOP_K
from fastapi import HTTPException, Request

from app.features.workspace.course_tests.service import FewShotSearchService


def get_few_shot_search_service(request: Request) -> FewShotSearchService:
    store = request.app.state.vector_store
    if store is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Vector index is not loaded. "
                "Run scripts/sync_question_vectors.py to build data/vector_index."
            ),
        )
    return FewShotSearchService(vector_store=store, top_k=SEARCH_TOP_K)
