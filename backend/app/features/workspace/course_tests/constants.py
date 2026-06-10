from pathlib import Path

from app.config import settings

SEARCH_TOP_K = 3
COURSE_TESTS_INDEX_DIR = Path(settings.data_dir) / "course_tests"
