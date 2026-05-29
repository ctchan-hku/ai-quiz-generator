from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domains.questions.constants import DISTRIBUTABLE_QUESTION_TYPES
from app.domains.questions.repository import (
    QUESTION_PROJECTION,
    QuestionRepository,
)


def _question_doc(question_id: str, prompt: str) -> dict:
    return {
        "_id": question_id,
        "prompt": prompt,
        "interface": {"name": "Multiple Choice"},
        "response_nrl": {
            "specification": [
                {"label": "A", "value": 0},
                {"label": "B", "value": 1},
            ]
        },
    }


@pytest.mark.asyncio
async def test_stream_all_unique():
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__.return_value = collection

    collection.aggregate.return_value.to_list = AsyncMock(
        return_value=[
            {
                "stats": [{"total": 3}],
                "unique": [
                    _question_doc("older", "Same prompt?"),
                    _question_doc("solo", "Unique prompt?"),
                ],
            }
        ]
    )

    repo = QuestionRepository(db)
    records, total = await repo.stream_all_unique()

    pipeline = collection.aggregate.call_args[0][0]
    assert pipeline[0]["$match"]["interface.name"]["$in"] == list(
        DISTRIBUTABLE_QUESTION_TYPES
    )
    assert pipeline[0]["$match"]["prompt"] == {"$type": "string"}
    assert pipeline[1] == {
        "$addFields": {"_prompt_key": {"$trim": {"input": "$prompt"}}}
    }
    assert pipeline[2] == {"$match": {"_prompt_key": {"$ne": ""}}}
    assert pipeline[-1]["$facet"]["unique"][-1]["$project"] == QUESTION_PROJECTION
    assert total == 3
    assert len(records) == 2
    assert records[0].id == "older"
    assert records[0].prompt == "Same prompt?"
    assert records[1].id == "solo"


@pytest.mark.asyncio
async def test_stream_all_unique_when_empty():
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__.return_value = collection
    collection.aggregate.return_value.to_list = AsyncMock(return_value=[])

    repo = QuestionRepository(db)
    records, total = await repo.stream_all_unique()

    assert records == []
    assert total == 0
