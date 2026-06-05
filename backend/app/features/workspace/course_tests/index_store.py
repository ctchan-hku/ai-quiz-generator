from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.features.workspace.course_tests.constants import (
    FAISS_DOCSTORE_FILENAME,
    FAISS_INDEX_FILENAME,
)
from app.features.workspace.course_tests.models import IndexedQuestion
from app.features.workspace.embedder import get_embedding_model


def index_dir() -> Path:
    return Path(settings.vector_index_dir)


def index_exists() -> bool:
    directory = index_dir()
    return (directory / FAISS_INDEX_FILENAME).exists() and (
        directory / FAISS_DOCSTORE_FILENAME
    ).exists()


def save_index(documents: list[Document]) -> None:
    directory = index_dir()
    directory.mkdir(parents=True, exist_ok=True)
    embeddings = get_embedding_model()
    store = FAISS.from_documents(documents, embeddings)
    store.save_local(str(directory), index_name="index")


def load_index() -> FAISS:
    embeddings = get_embedding_model()
    return FAISS.load_local(
        str(index_dir()),
        embeddings,
        index_name="index",
        allow_dangerous_deserialization=True,
    )


def documents_from_indexed_questions(
    questions: list[IndexedQuestion],
    *,
    page_content_by_id: dict[str, str],
) -> list[Document]:
    return [
        Document(
            page_content=page_content_by_id[question.question_id],
            metadata={
                "question_id": question.question_id,
                "prompt": question.prompt,
                "options": question.options,
            },
        )
        for question in questions
        if question.question_id in page_content_by_id
    ]
