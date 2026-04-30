"""Load JSON from a UTF-8 file."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def read_json(path: Path) -> Any:
    if not path.is_file():
        logger.warning("Missing JSON file: %s", path)
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        logger.warning("Cannot read JSON %s: %s", path, e)
        return {}
