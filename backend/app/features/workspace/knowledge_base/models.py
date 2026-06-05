from datetime import datetime

from pydantic import BaseModel, Field

from app.features.workspace.core.models import SearchResult


class _KnowledgeDocumentFields(BaseModel):
    id: str
    filename: str
    is_active: bool
    chunk_count: int


class KnowledgeDocumentSummary(_KnowledgeDocumentFields):
    pass


class KnowledgeDocument(_KnowledgeDocumentFields):
    user_id: str
    chunk_count: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime


class KnowledgeChunkResult(SearchResult):
    document_id: str
    filename: str
    chunk_id: str
    content: str
    page_number: int
