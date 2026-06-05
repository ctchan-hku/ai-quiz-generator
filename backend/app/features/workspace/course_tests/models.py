from pydantic import BaseModel, Field

from app.features.workspace.core.models import SearchResult


class IndexedQuestion(BaseModel):
    question_id: str
    prompt: str
    options: list[str] = Field(default_factory=list)


class SimilarityMatch(IndexedQuestion, SearchResult):
    pass


class SimilarityResult(BaseModel):
    index: int
    prompt: str
    matches: list[SimilarityMatch]
