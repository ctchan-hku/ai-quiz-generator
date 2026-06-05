import uuid
from datetime import datetime, timezone

from app.features.workspace.document_ingestion.pipeline import DocumentPipeline
from app.features.workspace.knowledge_base.constants import SEARCH_TOP_K
from app.features.workspace.knowledge_base.metadata_store import KnowledgeMetadataStore
from app.features.workspace.knowledge_base.models import (
    KnowledgeChunkResult,
    KnowledgeDocument,
    KnowledgeDocumentSummary,
)
from app.features.workspace.knowledge_base.vector_store import (
    add_to_user_index,
    delete_user_index,
    load_user_index,
)


class KnowledgeBaseService:
    def __init__(self, metadata_store: KnowledgeMetadataStore) -> None:
        self._metadata = metadata_store
        self._pipeline = DocumentPipeline()

    def ingest(
        self, pdf_bytes: bytes, filename: str, user_id: str
    ) -> KnowledgeDocumentSummary:
        document_id = str(uuid.uuid4())
        chunks = self._pipeline.process_bytes(pdf_bytes, document_id)
        add_to_user_index(user_id, chunks)
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
        self._metadata.insert(doc)
        return KnowledgeDocumentSummary(
            id=doc.id,
            filename=doc.filename,
            is_active=doc.is_active,
            chunk_count=doc.chunk_count,
        )

    def list_documents(self, user_id: str) -> list[KnowledgeDocumentSummary]:
        docs = self._metadata.find_by_user(user_id)
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
        doc = self._metadata.find_by_id(document_id)
        if doc is None:
            raise ValueError(f"Document {document_id} not found")
        self._metadata.set_active(document_id, is_active)
        updated = self._metadata.find_by_id(document_id)
        if updated is None:
            raise RuntimeError(f"Document {document_id} vanished after toggle")
        return KnowledgeDocumentSummary(
            id=updated.id,
            filename=updated.filename,
            is_active=updated.is_active,
            chunk_count=updated.chunk_count,
        )

    def delete_document(self, document_id: str) -> None:
        doc = self._metadata.find_by_id(document_id)
        if doc is None:
            raise ValueError(f"Document {document_id} not found")
        delete_user_index(doc.user_id)
        self._metadata.delete(document_id)

    def search(
        self, query: str, user_id: str
    ) -> list[KnowledgeChunkResult]:
        index = load_user_index(user_id)
        if index is None:
            return []
        active_ids = {d.id for d in self._metadata.find_active_by_user(user_id)}
        active_filenames = {
            d.id: d.filename
            for d in self._metadata.find_active_by_user(user_id)
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
