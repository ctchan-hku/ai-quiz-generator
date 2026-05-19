from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.modules.data.student_stats.repositories.response_repository import (
    RESPONSE_PROJECTION,
    TEMPLATE_TYPE_TEST,
    ResponseRepository,
)


@pytest.mark.parametrize(
    ("test_id", "expected_template_id"),
    [
        (
            "507f1f77bcf86cd799439011",
            {
                "$in": [
                    "507f1f77bcf86cd799439011",
                    ObjectId("507f1f77bcf86cd799439011"),
                ]
            },
        ),
        ("custom-test-id", "custom-test-id"),
    ],
)
def test_test_template_query(test_id: str, expected_template_id: object) -> None:
    assert ResponseRepository._test_template_query(test_id) == {
        "template.id": expected_template_id,
        "template.type": TEMPLATE_TYPE_TEST,
    }


def test_find_by_test_id_maps_id_and_answers() -> None:
    import asyncio

    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "answers": [{"question_id": "q1", "value": "A"}],
            },
            {"_id": "response-2"},
        ]
    )
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    repository = ResponseRepository(mock_db)
    result = asyncio.run(repository.find_by_test_id("507f1f77bcf86cd799439011"))

    assert len(result) == 2
    assert result[0].id == "507f1f77bcf86cd799439011"
    assert result[0].answers == [{"question_id": "q1", "value": "A"}]
    assert result[1].id == "response-2"
    assert result[1].answers == []
    mock_collection.find.assert_called_once_with(
        {
            "template.id": {
                "$in": [
                    "507f1f77bcf86cd799439011",
                    ObjectId("507f1f77bcf86cd799439011"),
                ]
            },
            "template.type": TEMPLATE_TYPE_TEST,
        },
        RESPONSE_PROJECTION,
    )
