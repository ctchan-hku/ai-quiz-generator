from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.features.auth.models import AuthenticatedUser
from app.features.auth.session_service import SessionService

_bearer = HTTPBearer()
INVALID_SESSION = "Invalid or expired session"


def get_session_service() -> SessionService:
    return SessionService(
        secret=settings.session_secret,
        ttl_days=settings.session_ttl_days,
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> AuthenticatedUser:
    user = session_service.resolve_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail=INVALID_SESSION)
    return user
