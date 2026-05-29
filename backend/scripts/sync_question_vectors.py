import asyncio
from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.domains.questions.repository import QuestionRepository
from app.features.similarity.index_store import save_index
from app.features.similarity.models import IndexedQuestion
from app.integrations.mongodb.client import create_motor_client


async def main() -> None:
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

    save_index(documents)
    duplicates_removed = total_embeddable - len(documents)
    print(
        f"Saved {len(documents)} unique vectors to "
        f"{Path(settings.vector_index_dir).resolve()} "
        f"({duplicates_removed} duplicate prompts skipped from {total_embeddable} embeddable)"
    )
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
