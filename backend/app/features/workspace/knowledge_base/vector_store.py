from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.features.workspace.core.vector_store import FaissIndexStore
from app.features.workspace.document_ingestion.models import DocumentChunk
from app.features.workspace.knowledge_base.constants import (
    KNOWLEDGE_BASE_INDEX_DIRNAME,
)


def _user_index_dir(user_id: str) -> Path:
    return Path(settings.vector_index_dir) / user_id / KNOWLEDGE_BASE_INDEX_DIRNAME


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


def _get_store(user_id: str) -> FaissIndexStore:
    return FaissIndexStore(_user_index_dir(user_id))


def user_index_exists(user_id: str) -> bool:
    return _get_store(user_id).exists()


def add_to_user_index(user_id: str, chunks: list[DocumentChunk]) -> None:
    _get_store(user_id).add(_chunks_to_documents(chunks))


def load_user_index(user_id: str):
    return _get_store(user_id).load()


def delete_user_index(user_id: str) -> None:
    _get_store(user_id).delete()
