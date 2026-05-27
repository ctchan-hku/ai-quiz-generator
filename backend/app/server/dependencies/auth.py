from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.auth.handler import LoginHandler
from app.modules.auth.repository import UserRepository
from app.modules.data.course_groups.repository import CourseGroupRepository
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository
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
