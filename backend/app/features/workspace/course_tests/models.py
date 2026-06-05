from pydantic import BaseModel, Field


class IndexedQuestion(BaseModel):
    question_id: str
    prompt: str
    options: list[str] = Field(default_factory=list)


class SimilarityMatch(IndexedQuestion):
    score: float


class SimilarityResult(BaseModel):
    index: int
    prompt: str
    matches: list[SimilarityMatch]
