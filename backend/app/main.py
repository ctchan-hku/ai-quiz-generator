import logging
import os

from app.server.factory import create_app

logging.basicConfig(level=logging.INFO)

if os.environ.get("APP_ENV", "prod") == "dev":
    logging.getLogger("openai._base_client").setLevel(logging.DEBUG)
    logging.getLogger("openai._base_client").setLevel(logging.DEBUG)

app = create_app()
