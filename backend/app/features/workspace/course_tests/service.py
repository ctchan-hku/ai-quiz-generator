from langchain_community.vectorstores import FAISS

from app.features.workspace.course_tests.constants import SEARCH_TOP_K
from app.features.workspace.course_tests.models import SimilarityMatch, SimilarityResult


class SimilarityService:
    def __init__(self, *, vector_store: FAISS, top_k: int = SEARCH_TOP_K) -> None:
        self._vector_store = vector_store
        self._top_k = top_k

    def find_similar_for_examples(self, examples: list[str]) -> list[SimilarityResult]:
        results: list[SimilarityResult] = []

        for index, example in enumerate(examples):
            prompt = example.strip()
            if not prompt:
                results.append(
                    SimilarityResult(
                        index=index,
                        prompt="",
                        matches=[],
                    )
                )
                continue

            scored_docs = self._vector_store.similarity_search_with_score(
                prompt,
                k=self._top_k,
            )
            matches = [
                SimilarityMatch(
                    question_id=str(document.metadata["question_id"]),
                    prompt=str(document.metadata["prompt"]),
                    options=list(document.metadata.get("options", [])),
                    score=float(score),
                )
                for document, score in scored_docs
            ]
            results.append(
                SimilarityResult(
                    index=index,
                    prompt=prompt,
                    matches=matches,
                )
            )

        return results
