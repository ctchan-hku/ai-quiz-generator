import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from app.features.workspace.core.index_store import FaissIndexStore
from app.features.workspace.core.vector_search import VectorSearchService
from app.features.workspace.document_ingestion.pipeline import DocumentPipeline
from app.features.workspace.knowledge_base.constants import (
    SEARCH_TOP_K,
    knowledge_base_user_index_dir,
)
from app.features.workspace.knowledge_base.models import (
    KnowledgeChunkResult,
    KnowledgeDocument,
    KnowledgeDocumentSummary,
)
from app.features.workspace.knowledge_base.repository import KnowledgeDocumentRepository
from app.features.workspace.knowledge_base.utils import chunks_to_documents


def _default_index_store_factory(user_id: str) -> FaissIndexStore:
    return FaissIndexStore(knowledge_base_user_index_dir(user_id))


def _default_vector_search_factory(user_id: str) -> VectorSearchService | None:
    index = _default_index_store_factory(user_id).load()
    if index is None:
        return None
    return VectorSearchService(vector_store=index, top_k=SEARCH_TOP_K)


class KnowledgeBaseService:
    def __init__(
        self,
        repository: KnowledgeDocumentRepository,
        *,
        index_store_factory: Callable[[str], FaissIndexStore] | None = None,
        vector_search_factory: Callable[[str], VectorSearchService | None]
        | None = None,
    ) -> None:
        self._repository = repository
        self._pipeline = DocumentPipeline()
        self._index_store_factory = index_store_factory or _default_index_store_factory
        self._vector_search_factory = (
            vector_search_factory or _default_vector_search_factory
        )

    def ingest(
        self, pdf_bytes: bytes, filename: str, user_id: str
    ) -> KnowledgeDocumentSummary:
        document_id = str(uuid.uuid4())
        chunks = self._pipeline.process_bytes(pdf_bytes, document_id)
        self._index_store_factory(user_id).add(chunks_to_documents(chunks))
        now = datetime.now(timezone.utc)
        doc = KnowledgeDocument(
            id=document_id,
            user_id=user_id,
            filename=filename,
            is_active=True,
            chunk_count=len(chunks),
            created_at=now,
            updated_at=now,
        )
        self._repository.insert(doc)
        return KnowledgeDocumentSummary(
            id=doc.id,
            filename=doc.filename,
            is_active=doc.is_active,
            chunk_count=doc.chunk_count,
        )

    def list_documents(self, user_id: str) -> list[KnowledgeDocumentSummary]:
        docs = self._repository.find_by_user(user_id)
        return [
            KnowledgeDocumentSummary(
                id=d.id,
                filename=d.filename,
                is_active=d.is_active,
                chunk_count=d.chunk_count,
            )
            for d in docs
        ]

    def toggle_document(
        self, document_id: str, is_active: bool
    ) -> KnowledgeDocumentSummary:
        doc = self._repository.find_by_id(document_id)
        if doc is None:
            raise ValueError(f"Document {document_id} not found")
        self._repository.set_active(document_id, is_active)
        updated = self._repository.find_by_id(document_id)
        if updated is None:
            raise RuntimeError(f"Document {document_id} vanished after toggle")
        return KnowledgeDocumentSummary(
            id=updated.id,
            filename=updated.filename,
            is_active=updated.is_active,
            chunk_count=updated.chunk_count,
        )

    def delete_document(self, document_id: str) -> None:
        doc = self._repository.find_by_id(document_id)
        if doc is None:
            raise ValueError(f"Document {document_id} not found")
        self._index_store_factory(doc.user_id).delete()
        self._repository.delete(document_id)

    def search(self, query: str, user_id: str) -> list[KnowledgeChunkResult]:
        searcher = self._vector_search_factory(user_id)
        if searcher is None:
            return []
        active_ids = {d.id for d in self._repository.find_active_by_user(user_id)}
        active_filenames = {
            d.id: d.filename for d in self._repository.find_active_by_user(user_id)
        }
        scored = searcher.search(
            query,
            filter_fn=lambda doc, _: (
                str(doc.metadata.get("document_id", "")) in active_ids
            ),
        )
        results: list[KnowledgeChunkResult] = []
        for document, score in scored:
            doc_id = str(document.metadata.get("document_id", ""))
            results.append(
                KnowledgeChunkResult(
                    document_id=doc_id,
                    filename=active_filenames.get(doc_id, ""),
                    chunk_id=str(document.metadata.get("chunk_id", "")),
                    content=document.page_content,
                    page_number=int(document.metadata.get("page_number", 1)),
                    score=float(score),
                )
            )
        return results
