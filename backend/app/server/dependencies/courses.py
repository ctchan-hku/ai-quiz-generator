from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.courses.repositories.course_group_repository import (
    CourseGroupRepository,
)
from app.modules.courses.services.course_group_service import CourseGroupService
from app.server.dependencies.mongodb import get_database


def get_course_group_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CourseGroupService:
    return CourseGroupService(CourseGroupRepository(db))
