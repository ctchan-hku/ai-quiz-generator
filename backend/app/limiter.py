from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.enable_rate_limiting,
    # Avoid reading project .env here: slowapi uses Starlette Config with system encoding;
    # UTF-8 characters in .env (e.g. em dash) fail on Windows cp950.
    config_filename="slowapi_limits.env",
)
