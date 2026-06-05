import tempfile
from pathlib import Path
from unittest.mock import patch

from app.features.workspace.knowledge_base import vector_store


def test_user_index_exists_returns_false_for_new_user():
    with (
        patch.object(vector_store, "_user_index_dir") as mock_dir,
        patch.object(vector_store, "get_embedding_model") as mock_embed,
    ):
        mock_dir.return_value = Path(tempfile.mkdtemp())
        mock_embed.return_value = None
        assert vector_store.user_index_exists("nonexistent") is False
