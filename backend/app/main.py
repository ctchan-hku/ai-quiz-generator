import logging

from app.config import settings
from app.server.factory import create_app

logging.basicConfig(level=logging.INFO)

if settings.log_openai_http_verbose:
    logging.getLogger("openai._base_client").setLevel(logging.DEBUG)

app = create_app()
