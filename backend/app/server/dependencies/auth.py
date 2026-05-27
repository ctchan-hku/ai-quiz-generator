from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.course_groups.repository import CourseGroupRepository
from app.modules.course_groups.service import CourseGroupService
from app.modules.data.auth.handlers.login_handler import LoginHandler
from app.modules.data.auth.repositories.user_repository import UserRepository
from app.modules.questions.repository import QuestionRepository
from app.modules.tests.repository import TestRepository
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
