from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.student_stats.repositories.course_group_repository import (
    CourseGroupRepository,
)
from app.modules.data.student_stats.repositories.test_repository import TestRepository
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)
from app.modules.data.student_stats.services.test_service import TestService
from app.server.dependencies.mongodb import get_database


def get_course_group_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CourseGroupService:
    return CourseGroupService(CourseGroupRepository(db))


def get_test_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> TestService:
    return TestService(TestRepository(db))
