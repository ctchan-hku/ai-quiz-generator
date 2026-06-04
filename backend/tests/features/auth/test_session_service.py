from datetime import UTC, datetime, timedelta

import jwt

from app.features.auth.session_service import SessionService


def test_create_and_resolve_round_trip() -> None:
    service = SessionService(secret="test-secret", ttl_days=7)
    token = service.create_session("user-1", "alice")
    user = service.resolve_token(token)
    assert user is not None
    assert user.user_id == "user-1"
    assert user.username == "alice"


def test_resolve_rejects_invalid_token() -> None:
    service = SessionService(secret="test-secret")
    assert service.resolve_token("not-a-jwt") is None


def test_resolve_rejects_wrong_secret() -> None:
    token = SessionService(secret="a").create_session("1", "u")
    assert SessionService(secret="b").resolve_token(token) is None


def test_resolve_rejects_expired_token() -> None:
    secret = "test-secret"
    expired = jwt.encode(
        {
            "sub": "user-1",
            "username": "alice",
            "exp": datetime.now(UTC) - timedelta(seconds=1),
            "iat": datetime.now(UTC) - timedelta(days=1),
        },
        secret,
        algorithm="HS256",
    )
    assert SessionService(secret=secret).resolve_token(expired) is None
