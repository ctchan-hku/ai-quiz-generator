import asyncio
from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.domains.questions.repository import QuestionRepository
from app.features.similarity.index_store import save_index
from app.features.similarity.models import IndexedQuestion
from app.features.similarity.prompts import format_embeddable_question
from app.integrations.mongodb.client import create_motor_client


async def main() -> None:
    if not settings.mongodb_uri:
        raise SystemExit("MONGODB_URI is required for sync")

    client = create_motor_client(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]
    repository = QuestionRepository(db)

    documents: list[Document] = []
    skipped = 0

    for record in await repository.stream_all():
        options = [item.label for item in record.response_nrl.specification]
        text = format_embeddable_question(prompt=record.prompt or "", options=options)
        if not text:
            skipped += 1
            continue

        indexed = IndexedQuestion(
            question_id=record.id,
            prompt=record.prompt or "",
            options=options,
        )
        documents.append(
            Document(
                page_content=text,
                metadata=indexed.model_dump(),
            )
        )

    if not documents:
        raise SystemExit("No embeddable questions found")

    save_index(documents)
    print(
        f"Saved {len(documents)} vectors to {Path(settings.vector_index_dir).resolve()} "
        f"(skipped {skipped})"
    )
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
