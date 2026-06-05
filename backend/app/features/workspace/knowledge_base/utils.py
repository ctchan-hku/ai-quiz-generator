from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.features.workspace.core.index_store import FaissIndexStore
from app.features.workspace.document_ingestion.models import DocumentChunk
from app.features.workspace.knowledge_base.constants import (
    KNOWLEDGE_BASE_INDEX_DIRNAME,
)


def _build_user_store(user_id: str) -> FaissIndexStore:
    index_dir = Path(settings.vector_index_dir) / user_id / KNOWLEDGE_BASE_INDEX_DIRNAME
    return FaissIndexStore(index_dir)


def _chunks_to_documents(chunks: list[DocumentChunk]) -> list[Document]:
    return [
        Document(
            page_content=chunk.content,
            metadata={
                "document_id": chunk.document_id or "",
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
            },
        )
        for chunk in chunks
    ]
