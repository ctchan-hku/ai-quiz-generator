from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.generation.models import GeneratedTest, MultipleChoiceQuestion


class GenerateTestRequest(BaseModel):
    topic: str = Field(default="", max_length=2000)
    num_questions: int = Field(10, ge=1, le=10)
    model: str
    few_shot_examples: list[str] | None = None
    user_instructions: list[str] | None = None
    pipeline_version: Literal[1, 2] = 2
    selected_test_ids: list[str] = Field(default_factory=list)

    @field_validator("topic")
    @classmethod
    def strip_topic(cls, v: object) -> str:
        if not isinstance(v, str):
            raise TypeError("topic must be a string")
        return v.strip()

    @model_validator(mode="after")
    def require_topic_or_few_shot(self) -> GenerateTestRequest:
        if self.topic:
            return self
        raw = self.few_shot_examples
        if raw and any(isinstance(s, str) and s.strip() for s in raw):
            return self
        raise ValueError(
            "Provide a non-empty topic or at least one non-empty few_shot_examples entry."
        )


class GenerateTestResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    questions: list[MultipleChoiceQuestion]
    model_used: str
    cost_usd: float = Field(ge=0)

    @classmethod
    def from_generated_test(
        cls,
        generated_test: GeneratedTest,
        *,
        model_used: str,
        cost_usd: float,
    ) -> GenerateTestResponse:
        return cls(
            questions=generated_test.questions,
            model_used=model_used,
            cost_usd=cost_usd,
        )
