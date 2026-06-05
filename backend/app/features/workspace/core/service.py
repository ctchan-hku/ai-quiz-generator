from collections.abc import Callable

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorSearchService:
    def __init__(self, vector_store: FAISS, top_k: int) -> None:
        self._vector_store = vector_store
        self._top_k = top_k

    def search(
        self,
        query: str,
        *,
        filter_fn: Callable[[Document, float], bool] | None = None,
    ) -> list[tuple[Document, float]]:
        scored = self._vector_store.similarity_search_with_score(query, k=self._top_k)
        if filter_fn is None:
            return scored
        return [(doc, score) for doc, score in scored if filter_fn(doc, score)]

    def search_batch(
        self,
        queries: list[str],
        *,
        filter_fn: Callable[[Document, float], bool] | None = None,
    ) -> list[list[tuple[Document, float]]]:
        return [self.search(q, filter_fn=filter_fn) for q in queries]
