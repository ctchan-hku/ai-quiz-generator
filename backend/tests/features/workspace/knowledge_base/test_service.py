from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.features.workspace.knowledge_base.models import KnowledgeDocument
from app.features.workspace.knowledge_base.service import KnowledgeBaseService


class TestListDocuments:
    def test_returns_empty_for_new_user(self):
        store = MagicMock()
        store.find_by_user.return_value = []
        with patch(
            "app.features.workspace.knowledge_base.service.KnowledgeMetadataStore",
            return_value=store,
        ):
            service = KnowledgeBaseService(metadata_store=store)
            result = service.list_documents("user-x")
            assert result == []

    def test_returns_summaries(self):
        store = MagicMock()
        now = datetime.now(timezone.utc)
        store.find_by_user.return_value = [
            KnowledgeDocument(
                id="d1",
                user_id="u1",
                filename="a.pdf",
                is_active=True,
                chunk_count=3,
                created_at=now,
                updated_at=now,
            ),
        ]
        with patch(
            "app.features.workspace.knowledge_base.service.KnowledgeMetadataStore",
            return_value=store,
        ):
            service = KnowledgeBaseService(metadata_store=store)
            result = service.list_documents("u1")
            assert len(result) == 1
            assert result[0].id == "d1"
            assert result[0].filename == "a.pdf"
            assert result[0].is_active is True


class TestToggleDocument:
    def test_toggle_flips_active_flag(self):
        store = MagicMock()
        now = datetime.now(timezone.utc)
        doc = KnowledgeDocument(
            id="d1",
            user_id="u1",
            filename="a.pdf",
            is_active=True,
            chunk_count=1,
            created_at=now,
            updated_at=now,
        )
        store.find_by_id.return_value = doc
        with patch(
            "app.features.workspace.knowledge_base.service.KnowledgeMetadataStore",
            return_value=store,
        ):
            service = KnowledgeBaseService(metadata_store=store)
            result = service.toggle_document("d1", False)
            store.set_active.assert_called_once_with("d1", False)
            assert result.is_active is not None
