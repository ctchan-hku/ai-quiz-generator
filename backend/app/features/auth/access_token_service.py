import jwt
from jwt.exceptions import InvalidTokenError


class AccessTokenService:
    def __init__(self, secret: str) -> None:
        self._secret = secret

    def resolve_user_id(self, token: str) -> str | None:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
            )
        except InvalidTokenError:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        return str(user_id)
