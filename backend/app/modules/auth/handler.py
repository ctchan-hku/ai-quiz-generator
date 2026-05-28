import bcrypt
from fastapi import HTTPException

from app.modules.auth.models import LoginRequest, LoginResult
from app.modules.auth.repository import UserRepository

INVALID_CREDENTIALS = "Invalid credentials"


class LoginHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def login(self, request: LoginRequest) -> LoginResult:
        user = await self._user_repository.find_by_username(request.username)
        if user is None or not self._password_matches(
            request.password,
            user["password"],
        ):
            raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)

        return LoginResult(
            user_id=str(user["_id"]),
            username=user["username"],
        )

    @staticmethod
    def _password_matches(plain_password: str, stored_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            stored_password.encode("utf-8"),
        )
