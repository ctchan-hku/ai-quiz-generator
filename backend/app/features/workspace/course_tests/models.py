from pydantic import BaseModel, Field

from app.features.workspace.core.models import SearchResult


class IndexedQuestion(BaseModel):
    question_id: str
    prompt: str
    options: list[str] = Field(default_factory=list)


class FewShotMatch(IndexedQuestion, SearchResult):
    pass


class FewShotResult(BaseModel):
    index: int
    prompt: str
    matches: list[FewShotMatch]
