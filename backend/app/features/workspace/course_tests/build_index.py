import logging

from langchain_core.documents import Document

from app.config import settings
from app.domains.questions.repository import QuestionRepository
from app.features.workspace.core.index_store import FaissIndexStore
from app.features.workspace.course_tests.constants import COURSE_TESTS_INDEX_DIR
from app.features.workspace.course_tests.models import IndexedQuestion
from app.integrations.mongodb.client import create_motor_client

logger = logging.getLogger(__name__)


async def build_course_tests_index() -> int:
    if not settings.mongodb_uri:
        raise RuntimeError(
            "MONGODB_URI is required to build the course-tests search index"
        )

    client = create_motor_client(settings.mongodb_uri)
    db = client[settings.database_name]
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
        logger.warning("No embeddable questions found; course-tests index not built")
        client.close()
        return 0

    index_dir = COURSE_TESTS_INDEX_DIR
    store = FaissIndexStore(index_dir)
    store.save(documents)
    duplicates_removed = total_embeddable - len(documents)
    logger.info(
        "Built course-tests search index at %s with %d questions "
        "(%d duplicate prompts skipped from %d embeddable)",
        index_dir.resolve(),
        len(documents),
        duplicates_removed,
        total_embeddable,
    )
    client.close()
    return len(documents)
