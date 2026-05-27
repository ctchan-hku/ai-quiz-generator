from pydantic import BaseModel, Field


class OptionMetric(BaseModel):
    label: str
    selection_rate: float
    cohort_attraction: list[float] = Field(default_factory=list)
    effectiveness: float | None = None


class QuestionMetric(BaseModel):
    question_id: str
    options: list[OptionMetric] = Field(default_factory=list)
    difficulty_index: list[float] = Field(default_factory=list)
    discrimination_index: list[float] = Field(default_factory=list)


class QuestionMetricsResponse(BaseModel):
    questions: list[QuestionMetric] = Field(default_factory=list)
