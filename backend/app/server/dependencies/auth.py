from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.features.auth.access_token_service import AccessTokenService
from app.features.auth.models import AuthenticatedUser
from app.features.auth.repository import UserRepository
from app.server.dependencies.mongodb import get_database

_bearer = HTTPBearer()
INVALID_ACCESS_TOKEN = "Invalid or expired access token"


def get_access_token_service() -> AccessTokenService:
    return AccessTokenService(secret=settings.access_token_secret)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    token_service: Annotated[AccessTokenService, Depends(get_access_token_service)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> AuthenticatedUser:
    user_id = token_service.resolve_user_id(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail=INVALID_ACCESS_TOKEN)

    user = await UserRepository(db).find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail=INVALID_ACCESS_TOKEN)

    return AuthenticatedUser(user_id=user_id, username=user["username"])
