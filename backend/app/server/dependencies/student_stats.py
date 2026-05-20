from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.student_stats.handlers.list_tests_handler import ListTestsHandler
from app.modules.data.student_stats.handlers.question_metrics_handler import (
    QuestionMetricsHandler,
)
from app.modules.data.student_stats.repositories.course_group_repository import (
    CourseGroupRepository,
)
from app.modules.data.student_stats.repositories.question_repository import (
    QuestionRepository,
)
from app.modules.data.student_stats.repositories.response_repository import (
    ResponseRepository,
)
from app.modules.data.student_stats.repositories.test_repository import TestRepository
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)
from app.modules.data.student_stats.services.response_service import ResponseService
from app.server.dependencies.mongodb import get_database


def get_course_group_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CourseGroupService:
    return CourseGroupService(CourseGroupRepository(db))


def get_list_tests_handler(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> ListTestsHandler:
    return ListTestsHandler(
        TestRepository(db),
        QuestionRepository(db),
    )


def get_response_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> ResponseService:
    return ResponseService(ResponseRepository(db))


def get_question_metrics_handler(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> QuestionMetricsHandler:
    return QuestionMetricsHandler(
        TestRepository(db),
        QuestionRepository(db),
        ResponseRepository(db),
    )
