from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.domains.questions.repository import QuestionRepository
from app.features.workspace.core.index_store import FaissIndexStore
from app.features.workspace.course_tests.constants import COURSE_TESTS_INDEX_DIRNAME
from app.features.workspace.course_tests.models import IndexedQuestion
from app.integrations.mongodb.client import create_motor_client


async def sync_question_index() -> None:
    if not settings.mongodb_uri:
        raise SystemExit("MONGODB_URI is required for sync")

    client = create_motor_client(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]
    repository = QuestionRepository(db)

    records, total_embeddable = await repository.stream_all_unique()
    documents: list[Document] = []

    for record in records:
        prompt = record.prompt.strip()
        options = [item.label for item in record.response_nrl.specification]
        indexed = IndexedQuestion(
            question_id=record.id,
            prompt=prompt,
            options=options,
        )
        documents.append(
            Document(
                page_content=prompt,
                metadata=indexed.model_dump(),
            )
        )

    if not documents:
        raise SystemExit("No embeddable questions found")

    index_dir = Path(settings.vector_index_dir) / COURSE_TESTS_INDEX_DIRNAME
    store = FaissIndexStore(index_dir)
    store.save(documents)
    duplicates_removed = total_embeddable - len(documents)
    print(
        f"Saved {len(documents)} unique vectors to "
        f"{index_dir.resolve()} "
        f"({duplicates_removed} duplicate prompts skipped from {total_embeddable} embeddable)"
    )
    client.close()
