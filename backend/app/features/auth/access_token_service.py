import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)


class AccessTokenError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AccessTokenService:
    def __init__(self, secret: str | None = None) -> None:
        self._secret = secret

    def resolve_user_id(self, token: str) -> str:
        payload = self._decode_payload(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise AccessTokenError("Access token is missing a user identifier")

        return str(user_id)

    def _decode_payload(self, token: str) -> dict[str, object]:
        try:
            if self._secret is not None:
                return jwt.decode(token, self._secret, algorithms=["HS256"])

            return jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": True},
                algorithms=["HS256"],
            )
        except ExpiredSignatureError as exc:
            raise AccessTokenError("Access token has expired") from exc
        except InvalidSignatureError as exc:
            raise AccessTokenError("Invalid access token signature") from exc
        except InvalidTokenError as exc:
            raise AccessTokenError("Invalid access token") from exc
