from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.data.questions.constants import DISTRIBUTABLE_QUESTION_TYPES
from app.modules.data.questions.repository import (
    QUESTION_PROJECTION,
    QuestionRepository,
)


@pytest.mark.asyncio
async def test_stream_all_yields_distributable_question_records():
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__.return_value = collection

    collection.find.return_value.to_list = AsyncMock(
        return_value=[
            {
                "_id": "abc123",
                "prompt": "Sample?",
                "interface": {"name": "Multiple Choice"},
                "response_nrl": {
                    "specification": [
                        {"label": "A", "value": 0},
                        {"label": "B", "value": 1},
                    ]
                },
            }
        ]
    )

    repo = QuestionRepository(db)
    records = await repo.stream_all()

    collection.find.assert_called_once_with(
        {"interface.name": {"$in": list(DISTRIBUTABLE_QUESTION_TYPES)}},
        QUESTION_PROJECTION,
    )
    assert len(records) == 1
    assert records[0].id == "abc123"
    assert records[0].prompt == "Sample?"
