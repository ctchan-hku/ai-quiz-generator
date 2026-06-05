import uuid
from datetime import datetime, timezone

from app.features.workspace.document_ingestion.pipeline import DocumentPipeline
from app.features.workspace.knowledge_base.constants import SEARCH_TOP_K
from app.features.workspace.knowledge_base.models import (
    KnowledgeChunkResult,
    KnowledgeDocument,
    KnowledgeDocumentSummary,
)
from app.features.workspace.knowledge_base.repository import KnowledgeDocumentRepository
from app.features.workspace.knowledge_base.utils import (
    _build_user_store,
    _chunks_to_documents,
)


class KnowledgeBaseService:
    def __init__(self, repository: KnowledgeDocumentRepository) -> None:
        self._repository = repository
        self._pipeline = DocumentPipeline()

    def ingest(
        self, pdf_bytes: bytes, filename: str, user_id: str
    ) -> KnowledgeDocumentSummary:
        document_id = str(uuid.uuid4())
        chunks = self._pipeline.process_bytes(pdf_bytes, document_id)
        _build_user_store(user_id).add(_chunks_to_documents(chunks))
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
        _build_user_store(doc.user_id).delete()
        self._repository.delete(document_id)

    def search(self, query: str, user_id: str) -> list[KnowledgeChunkResult]:
        index = _build_user_store(user_id).load()
        if index is None:
            return []
        active_ids = {d.id for d in self._repository.find_active_by_user(user_id)}
        active_filenames = {
            d.id: d.filename for d in self._repository.find_active_by_user(user_id)
        }
        scored = index.similarity_search_with_score(query, k=SEARCH_TOP_K)
        results: list[KnowledgeChunkResult] = []
        for document, score in scored:
            doc_id = str(document.metadata.get("document_id", ""))
            if doc_id not in active_ids:
                continue
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
