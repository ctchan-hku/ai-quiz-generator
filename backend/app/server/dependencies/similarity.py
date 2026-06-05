from fastapi import HTTPException, Request

from app.features.workspace.course_tests.service import SimilarityService


def get_similarity_service(request: Request) -> SimilarityService:
    store = request.app.state.similarity_vector_store
    if store is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Similarity index is not loaded. "
                "Run scripts/sync_question_vectors.py to build data/vector_index."
            ),
        )
    return SimilarityService(vector_store=store)
