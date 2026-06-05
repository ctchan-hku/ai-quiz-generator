from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.features.workspace.document_ingestion.types import DocumentChunk
from app.features.workspace.embedder import get_embedding_model
from app.features.workspace.knowledge_base.constants import (
    KNOWLEDGE_BASE_INDEX_DIRNAME,
)


def _user_index_dir(user_id: str) -> Path:
    return Path(settings.vector_index_dir) / user_id / KNOWLEDGE_BASE_INDEX_DIRNAME


def user_index_exists(user_id: str) -> bool:
    directory = _user_index_dir(user_id)
    return (directory / "index.faiss").exists() and (directory / "index.pkl").exists()


def build_user_index(user_id: str, chunks: list[DocumentChunk]) -> None:
    directory = _user_index_dir(user_id)
    directory.mkdir(parents=True, exist_ok=True)
    embeddings = get_embedding_model()
    documents = [
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
    store = FAISS.from_documents(documents, embeddings)
    store.save_local(str(directory), index_name="index")


def add_to_user_index(user_id: str, chunks: list[DocumentChunk]) -> None:
    embeddings = get_embedding_model()
    documents = [
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
    store = load_user_index(user_id)
    if store is None:
        store = FAISS.from_documents(documents, embeddings)
    else:
        store.add_documents(documents)
    directory = _user_index_dir(user_id)
    directory.mkdir(parents=True, exist_ok=True)
    store.save_local(str(directory), index_name="index")


def load_user_index(user_id: str) -> FAISS | None:
    if not user_index_exists(user_id):
        return None
    embeddings = get_embedding_model()
    return FAISS.load_local(
        str(_user_index_dir(user_id)),
        embeddings,
        index_name="index",
        allow_dangerous_deserialization=True,
    )


def delete_user_index(user_id: str) -> None:
    import shutil

    directory = _user_index_dir(user_id)
    if directory.exists():
        shutil.rmtree(directory)
