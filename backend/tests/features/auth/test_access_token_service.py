from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.features.auth.access_token_service import AccessTokenError, AccessTokenService


def _gear_access_token(
    *,
    user_id: str,
    secret: str = "any-secret",
    expired: bool = False,
) -> str:
    exp = datetime.now(UTC) + (timedelta(seconds=-1) if expired else timedelta(hours=1))
    return jwt.encode(
        {
            "authorized": True,
            "user_id": user_id,
            "uuid": "device-uuid",
            "exp": exp,
        },
        secret,
        algorithm="HS256",
    )


def test_resolve_user_id_without_secret() -> None:
    service = AccessTokenService()
    token = _gear_access_token(user_id="507f1f77bcf86cd799439011")
    assert service.resolve_user_id(token) == "507f1f77bcf86cd799439011"


def test_resolve_user_id_with_matching_secret() -> None:
    service = AccessTokenService(secret="test-access-secret")
    token = _gear_access_token(
        user_id="507f1f77bcf86cd799439011",
        secret="test-access-secret",
    )
    assert service.resolve_user_id(token) == "507f1f77bcf86cd799439011"


def test_resolve_rejects_invalid_token() -> None:
    service = AccessTokenService()
    with pytest.raises(AccessTokenError, match="Invalid access token"):
        service.resolve_user_id("not-a-jwt")


def test_resolve_rejects_wrong_secret_when_secret_configured() -> None:
    token = _gear_access_token(user_id="user-1", secret="secret-a")
    with pytest.raises(AccessTokenError, match="Invalid access token signature"):
        AccessTokenService(secret="secret-b").resolve_user_id(token)


def test_resolve_accepts_wrong_secret_when_secret_not_configured() -> None:
    token = _gear_access_token(user_id="user-1", secret="secret-a")
    assert AccessTokenService().resolve_user_id(token) == "user-1"


def test_resolve_rejects_expired_token() -> None:
    service = AccessTokenService()
    token = _gear_access_token(user_id="user-1", expired=True)
    with pytest.raises(AccessTokenError, match="Access token has expired"):
        service.resolve_user_id(token)


def test_resolve_rejects_missing_user_id_claim() -> None:
    token = jwt.encode(
        {"authorized": True, "uuid": "device-uuid"},
        "any-secret",
        algorithm="HS256",
    )
    with pytest.raises(AccessTokenError, match="missing a user identifier"):
        AccessTokenService().resolve_user_id(token)
