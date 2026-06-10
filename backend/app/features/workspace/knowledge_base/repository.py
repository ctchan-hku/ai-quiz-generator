import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.features.workspace.knowledge_base.constants import KNOWLEDGE_BASE_CATALOG_PATH
from app.features.workspace.knowledge_base.models import KnowledgeDocument


class KnowledgeDocumentRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = (
            Path(db_path) if db_path is not None else KNOWLEDGE_BASE_CATALOG_PATH
        )
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_kd_user_id "
                "ON knowledge_documents(user_id)"
            )

    def insert(self, document: KnowledgeDocument) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO knowledge_documents "
                "(id, user_id, filename, is_active, chunk_count, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    document.id,
                    document.user_id,
                    document.filename,
                    int(document.is_active),
                    document.chunk_count,
                    document.created_at.isoformat(),
                    document.updated_at.isoformat(),
                ),
            )

    def find_by_user(self, user_id: str) -> list[KnowledgeDocument]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM knowledge_documents WHERE user_id = ? "
                "ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [self._row_to_document(row) for row in rows]

    def find_by_id(self, document_id: str) -> KnowledgeDocument | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM knowledge_documents WHERE id = ?",
                (document_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_document(row)

    def find_active_by_user(self, user_id: str) -> list[KnowledgeDocument]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM knowledge_documents "
                "WHERE user_id = ? AND is_active = 1 "
                "ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [self._row_to_document(row) for row in rows]

    def set_active(self, document_id: str, is_active: bool) -> None:
        now = datetime.now(timezone.utc)
        with self._connect() as conn:
            conn.execute(
                "UPDATE knowledge_documents SET is_active = ?, updated_at = ? "
                "WHERE id = ?",
                (int(is_active), now.isoformat(), document_id),
            )

    def delete(self, document_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM knowledge_documents WHERE id = ?",
                (document_id,),
            )

    def _row_to_document(self, row: sqlite3.Row) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=row["id"],
            user_id=row["user_id"],
            filename=row["filename"],
            is_active=bool(row["is_active"]),
            chunk_count=row["chunk_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
