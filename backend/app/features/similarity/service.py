from langchain_community.vectorstores import FAISS

from app.config import settings
from app.features.similarity.models import (
    FewShotSimilarityResponse,
    FewShotSimilarityResult,
    SimilarQuestionMatch,
)


class SimilarityService:
    def __init__(self, *, vector_store: FAISS, top_k: int | None = None) -> None:
        self._vector_store = vector_store
        self._top_k = top_k or settings.similarity_top_k

    def find_similar_for_examples(
        self,
        examples: list[str],
    ) -> FewShotSimilarityResponse:
        results: list[FewShotSimilarityResult] = []

        for index, example in enumerate(examples):
            query_text = example.strip()
            if not query_text:
                results.append(
                    FewShotSimilarityResult(
                        example_index=index,
                        example="",
                        matches=[],
                    )
                )
                continue

            scored_docs = self._vector_store.similarity_search_with_score(
                query_text,
                k=self._top_k,
            )
            matches = [
                SimilarQuestionMatch(
                    question_id=str(document.metadata["question_id"]),
                    prompt=str(document.metadata["prompt"]),
                    options=list(document.metadata.get("options", [])),
                    score=float(score),
                )
                for document, score in scored_docs
            ]
            results.append(
                FewShotSimilarityResult(
                    example_index=index,
                    example=query_text,
                    matches=matches,
                )
            )

        return FewShotSimilarityResponse(results=results)
