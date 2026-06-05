from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.features.workspace.core.vector_store import FaissIndexStore
from app.features.workspace.course_tests.models import IndexedQuestion


_index_dir = Path(settings.vector_index_dir)
_store = FaissIndexStore(_index_dir)


def index_exists() -> bool:
    return _store.exists()


def save_index(documents: list[Document]) -> None:
    _store.save(documents)


def load_index():
    store = _store.load()
    if store is None:
        raise FileNotFoundError(
            f"No FAISS index found at {_index_dir.resolve()}"
        )
    return store


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
