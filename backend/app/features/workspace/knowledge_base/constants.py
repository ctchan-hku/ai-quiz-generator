from pathlib import Path

from app.config import settings

SEARCH_TOP_K = 5
KNOWLEDGE_BASE_CATALOG_PATH = Path(settings.data_dir) / "knowledge_base" / "catalog.db"


def knowledge_base_user_index_dir(user_id: str) -> Path:
    return Path(settings.data_dir) / "knowledge_base" / "users" / user_id
