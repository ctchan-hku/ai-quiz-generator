from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.auth.handlers.login_handler import LoginHandler
from app.modules.data.auth.repositories.user_repository import UserRepository
from app.modules.data.student_stats.repositories.course_group_repository import (
    CourseGroupRepository,
)
from app.modules.data.student_stats.repositories.question_repository import (
    QuestionRepository,
)
from app.modules.data.student_stats.repositories.test_repository import TestRepository
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)
from app.server.dependencies.mongodb import get_database


def get_login_handler(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> LoginHandler:
    return LoginHandler(
        UserRepository(db),
        CourseGroupService(CourseGroupRepository(db)),
        TestRepository(db),
        QuestionRepository(db),
    )
