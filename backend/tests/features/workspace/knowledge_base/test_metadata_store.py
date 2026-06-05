import tempfile
from datetime import datetime, timezone

from app.features.workspace.knowledge_base.metadata_store import KnowledgeMetadataStore
from app.features.workspace.knowledge_base.models import KnowledgeDocument


def test_insert_and_find_by_user():
    db_path = tempfile.mktemp(suffix=".db")
    store = KnowledgeMetadataStore(db_path=db_path)
    now = datetime.now(timezone.utc)
    doc = KnowledgeDocument(
        id="doc-1",
        user_id="user-a",
        filename="slides.pdf",
        is_active=True,
        chunk_count=3,
        created_at=now,
        updated_at=now,
    )
    store.insert(doc)
    results = store.find_by_user("user-a")
    assert len(results) == 1
    assert results[0].id == "doc-1"
    assert results[0].filename == "slides.pdf"


def test_set_active_toggles():
    db_path = tempfile.mktemp(suffix=".db")
    store = KnowledgeMetadataStore(db_path=db_path)
    now = datetime.now(timezone.utc)
    doc = KnowledgeDocument(
        id="doc-2",
        user_id="user-a",
        filename="exam.pdf",
        is_active=True,
        chunk_count=1,
        created_at=now,
        updated_at=now,
    )
    store.insert(doc)
    store.set_active("doc-2", False)
    found = store.find_by_id("doc-2")
    assert found is not None
    assert found.is_active is False


def test_find_active_by_user_excludes_inactive():
    db_path = tempfile.mktemp(suffix=".db")
    store = KnowledgeMetadataStore(db_path=db_path)
    now = datetime.now(timezone.utc)
    store.insert(
        KnowledgeDocument(
            id="active",
            user_id="u1",
            filename="a.pdf",
            is_active=True,
            chunk_count=1,
            created_at=now,
            updated_at=now,
        )
    )
    store.insert(
        KnowledgeDocument(
            id="inactive",
            user_id="u1",
            filename="b.pdf",
            is_active=False,
            chunk_count=1,
            created_at=now,
            updated_at=now,
        )
    )
    active = store.find_active_by_user("u1")
    assert len(active) == 1
    assert active[0].id == "active"
