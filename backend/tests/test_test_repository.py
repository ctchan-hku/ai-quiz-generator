from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.modules.data.student_stats.repositories.test_repository import TestRepository


@pytest.mark.parametrize(
    ("course_group_id", "expected_id"),
    [
        (
            "613cc5cfe3004e7cb7c267e8",
            {
                "$in": [
                    "613cc5cfe3004e7cb7c267e8",
                    ObjectId("613cc5cfe3004e7cb7c267e8"),
                ]
            },
        ),
        ("custom-group-id", "custom-group-id"),
    ],
)
def test_course_group_query(course_group_id: str, expected_id: object) -> None:
    assert TestRepository._course_group_query(course_group_id) == {
        "course_group_details.id": expected_id
    }


def test_find_by_course_group_id_maps_fields() -> None:
    import asyncio

    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "Quiz 1",
                "questions": [{"id": "q1"}],
                "grade_cutoff": [{"grade": "A", "cutoff": 90}],
            },
            {"_id": "test-2", "name": "Quiz 2"},
        ]
    )
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    repository = TestRepository(mock_db)
    result = asyncio.run(repository.find_by_course_group_id("613cc5cfe3004e7cb7c267e8"))

    assert len(result) == 2
    assert result[0].id == "507f1f77bcf86cd799439011"
    assert result[0].name == "Quiz 1"
    assert result[0].questions == [{"id": "q1"}]
    assert result[0].grade_cutoff == [{"grade": "A", "cutoff": 90}]
    assert result[1].questions == []
    assert result[1].grade_cutoff == []
