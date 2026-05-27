from typing import Annotated

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.course_groups.repository import CourseGroupRepository
from app.modules.course_groups.service import CourseGroupService
from app.modules.data.student_stats.handlers.question_metrics_handler import (
    QuestionMetricsHandler,
)
from app.modules.data.student_stats.services.question_metrics_service import (
    QuestionMetricsService,
)
from app.modules.questions.repository import QuestionRepository
from app.modules.responses.repository import ResponseRepository
from app.modules.responses.service import ResponseService
from app.modules.tests.repository import TestRepository
from app.modules.tests.service import TestService
from app.server.dependencies.mongodb import get_database


def get_course_group_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CourseGroupService:
    return CourseGroupService(CourseGroupRepository(db))


def get_test_service(request: Request) -> TestService:
    db = request.app.state.mongodb_database
    repository = TestRepository(db) if db is not None else None
    return TestService(repository)


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
        QuestionMetricsService(),
    )


def get_optional_question_metrics_handler(
    request: Request,
) -> QuestionMetricsHandler | None:
    db = request.app.state.mongodb_database
    if db is None:
        return None
    return QuestionMetricsHandler(
        TestRepository(db),
        QuestionRepository(db),
        ResponseRepository(db),
        QuestionMetricsService(),
    )
