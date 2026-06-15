from slowapi import Limiter
from slowapi.util import get_remote_address

from app.server.constants import ENABLE_RATE_LIMITING

limiter = Limiter(
    key_func=get_remote_address,
    enabled=ENABLE_RATE_LIMITING,
)
