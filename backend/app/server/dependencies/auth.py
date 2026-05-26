from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.auth.repositories.user_repository import UserRepository
from app.modules.data.auth.services.login_service import LoginService
from app.modules.data.student_stats.repositories.course_group_repository import (
    CourseGroupRepository,
)
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)
from app.server.dependencies.mongodb import get_database


def get_login_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> LoginService:
    return LoginService(
        UserRepository(db),
        CourseGroupService(CourseGroupRepository(db)),
    )
