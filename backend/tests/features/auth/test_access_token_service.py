from datetime import UTC, datetime, timedelta

import jwt

from app.features.auth.access_token_service import AccessTokenService


def _cms_token(secret: str, *, user_id: str, expired: bool = False) -> str:
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


def test_resolve_user_id_from_cms_token() -> None:
    service = AccessTokenService(secret="test-access-secret")
    token = _cms_token("test-access-secret", user_id="507f1f77bcf86cd799439011")
    assert service.resolve_user_id(token) == "507f1f77bcf86cd799439011"


def test_resolve_rejects_invalid_token() -> None:
    service = AccessTokenService(secret="test-access-secret")
    assert service.resolve_user_id("not-a-jwt") is None


def test_resolve_rejects_wrong_secret() -> None:
    token = _cms_token("secret-a", user_id="user-1")
    assert AccessTokenService(secret="secret-b").resolve_user_id(token) is None


def test_resolve_rejects_expired_token() -> None:
    service = AccessTokenService(secret="test-access-secret")
    token = _cms_token(
        "test-access-secret",
        user_id="user-1",
        expired=True,
    )
    assert service.resolve_user_id(token) is None


def test_resolve_rejects_missing_user_id_claim() -> None:
    token = jwt.encode(
        {"authorized": True, "uuid": "device-uuid"},
        "test-access-secret",
        algorithm="HS256",
    )
    assert (
        AccessTokenService(secret="test-access-secret").resolve_user_id(token) is None
    )
