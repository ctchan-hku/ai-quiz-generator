import logging

from app.env import is_non_prod
from app.server.factory import create_app

logging.basicConfig(level=logging.INFO)

if is_non_prod():
    logging.getLogger("openai._base_client").setLevel(logging.DEBUG)

app = create_app()
