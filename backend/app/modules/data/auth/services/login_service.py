import bcrypt
from fastapi import HTTPException

from app.modules.data.auth.models import LoginRequest, LoginResponse
from app.modules.data.auth.repositories.user_repository import UserRepository
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)

INVALID_CREDENTIALS = "Invalid credentials"


class LoginService:
    def __init__(
        self,
        user_repository: UserRepository,
        course_group_service: CourseGroupService,
    ) -> None:
        self._user_repository = user_repository
        self._course_group_service = course_group_service

    async def login(self, request: LoginRequest) -> LoginResponse:
        user = await self._user_repository.find_by_username(request.username)
        if user is None or not self._password_matches(request.password, user["password"]):
            raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)

        user_id = str(user["_id"])
        course_groups = await self._course_group_service.list_by_user_id(user_id)
        return LoginResponse(
            user_id=user_id,
            username=user["username"],
            course_groups=course_groups.course_groups,
        )

    @staticmethod
    def _password_matches(plain_password: str, stored_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            stored_password.encode("utf-8"),
        )
