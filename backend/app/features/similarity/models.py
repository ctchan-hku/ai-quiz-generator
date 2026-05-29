from pydantic import BaseModel, Field


class IndexedQuestion(BaseModel):
    question_id: str
    prompt: str
    options: list[str] = Field(default_factory=list)


class FewShotExample(BaseModel):
    question: str
    options: list[str] = Field(default_factory=list)


class SimilarQuestionMatch(BaseModel):
    question_id: str
    prompt: str
    options: list[str]
    score: float


class FewShotSimilarityResult(BaseModel):
    example_index: int
    query_text: str
    matches: list[SimilarQuestionMatch]


class FewShotSimilarityRequest(BaseModel):
    examples: list[FewShotExample] = Field(min_length=1)


class FewShotSimilarityResponse(BaseModel):
    results: list[FewShotSimilarityResult]
