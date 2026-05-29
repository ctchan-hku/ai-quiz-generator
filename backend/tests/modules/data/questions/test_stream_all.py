import pytest
from unittest.mock import AsyncMock, MagicMock

from app.modules.data.questions.repository import QuestionRepository


@pytest.mark.asyncio
async def test_stream_all_yields_question_records():
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__.return_value = collection

    collection.find.return_value.to_list = AsyncMock(
        return_value=[
            {
                "_id": "abc123",
                "prompt": "Sample?",
                "interface": {"name": "multiple_choice"},
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

    assert len(records) == 1
    assert records[0].id == "abc123"
    assert records[0].prompt == "Sample?"
