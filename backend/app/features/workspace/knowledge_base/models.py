from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str
    user_id: str
    filename: str
    is_active: bool
    chunk_count: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentSummary(BaseModel):
    id: str
    filename: str
    is_active: bool
    chunk_count: int


class KnowledgeChunkResult(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    content: str
    page_number: int
    score: float
