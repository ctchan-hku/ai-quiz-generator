from pydantic import BaseModel, Field


class IndexedQuestion(BaseModel):
    question_id: str
    prompt: str
    options: list[str] = Field(default_factory=list)


class SimilarQuestionMatch(BaseModel):
    question_id: str
    prompt: str
    options: list[str]
    score: float


class FewShotSimilarityResult(BaseModel):
    example_index: int
    example: str
    matches: list[SimilarQuestionMatch]


class FewShotSimilarityRequest(BaseModel):
    examples: list[str] = Field(min_length=1)


class FewShotSimilarityResponse(BaseModel):
    results: list[FewShotSimilarityResult]
