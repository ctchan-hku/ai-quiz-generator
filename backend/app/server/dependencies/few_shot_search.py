from fastapi import HTTPException, Request

from app.features.workspace.course_tests.constants import SEARCH_TOP_K
from app.features.workspace.course_tests.service import FewShotSearchService


def get_few_shot_search_service(request: Request) -> FewShotSearchService:
    store = request.app.state.vector_store
    if store is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Course-tests search index is not loaded. "
                "Run scripts/build_course_tests_index.py after importing new questions into MongoDB."
            ),
        )
    return FewShotSearchService(vector_store=store, top_k=SEARCH_TOP_K)
