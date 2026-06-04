from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from app.features.auth.models import AuthenticatedUser

SESSION_TTL_DAYS = 7


class SessionService:
    def __init__(self, secret: str, ttl_days: int = SESSION_TTL_DAYS) -> None:
        self._secret = secret
        self._ttl = timedelta(days=ttl_days)

    def create_session(self, user_id: str, username: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "username": username,
            "exp": now + self._ttl,
            "iat": now,
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    def resolve_token(self, token: str) -> AuthenticatedUser | None:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
            )
        except InvalidTokenError:
            return None
        user_id = payload.get("sub")
        username = payload.get("username")
        if not user_id or not username:
            return None
        return AuthenticatedUser(user_id=str(user_id), username=str(username))
