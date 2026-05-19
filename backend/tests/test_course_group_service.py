from unittest.mock import AsyncMock, MagicMock

from app.modules.courses.models import CourseGroupSummary
from app.modules.courses.services.course_group_service import CourseGroupService


def test_list_owned_by_user_filters_copy_and_fake() -> None:
    import asyncio

    mock_repository = MagicMock()
    mock_repository.find_owned_by_user = AsyncMock(
        return_value=[
            CourseGroupSummary(id="1", name="MATH1013 2021-2022 Sem 1 - 1"),
            CourseGroupSummary(id="2", name="COPY - MATH1013 2021-2022 Sem 1 - 1"),
            CourseGroupSummary(id="3", name="Fake demo"),
        ]
    )

    service = CourseGroupService(mock_repository)
    response = asyncio.run(service.list_owned_by_user("user-123"))

    assert [group.id for group in response.course_groups] == ["1"]
