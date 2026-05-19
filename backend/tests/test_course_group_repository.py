from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.modules.courses.repositories.course_group_repository import (
    CourseGroupRepository,
)


@pytest.mark.parametrize(
    ("user_id", "expected_owner"),
    [
        ("user-123", "user-123"),
        (
            "507f1f77bcf86cd799439011",
            {"$in": ["507f1f77bcf86cd799439011", ObjectId("507f1f77bcf86cd799439011")]},
        ),
    ],
)
def test_owner_query(user_id: str, expected_owner: object) -> None:
    assert CourseGroupRepository._owner_query(user_id) == {"owner": expected_owner}


async def _collect_cursor(documents: list[dict]) -> list[dict]:
    for document in documents:
        yield document


def test_find_owned_by_user_maps_id_and_name() -> None:
    import asyncio

    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(
        return_value=[
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Algebra"},
            {"_id": "cg-2", "name": "Biology"},
        ]
    )
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    repository = CourseGroupRepository(mock_db)
    result = asyncio.run(repository.find_owned_by_user("user-123"))

    assert len(result) == 2
    assert result[0].id == "507f1f77bcf86cd799439011"
    assert result[0].name == "Algebra"
    assert result[1].id == "cg-2"
    assert result[1].name == "Biology"
    mock_collection.find.assert_called_once_with(
        {"owner": "user-123"},
        {"_id": 1, "name": 1},
    )
