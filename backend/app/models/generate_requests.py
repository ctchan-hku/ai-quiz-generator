"""Pydantic bodies for generate routes (kept separate from routers for light test imports)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.mc_question import MultipleChoiceQuestion


class GenerateQuizRequest(BaseModel):
    topic: str = Field(default="", max_length=2000)
    num_questions: int = Field(10, ge=0, le=10)
    model: str
    few_shot_examples: list[str] | None = None
    user_instructions: list[str] | None = None
    pipeline_version: Literal[1, 2] = 2

    @field_validator("topic")
    @classmethod
    def strip_topic(cls, v: object) -> str:
        if not isinstance(v, str):
            raise TypeError("topic must be a string")
        return v.strip()

    @model_validator(mode="after")
    def require_topic_or_few_shot(self) -> GenerateQuizRequest:
        if self.topic:
            return self
        raw = self.few_shot_examples
        if raw and any(isinstance(s, str) and s.strip() for s in raw):
            return self
        raise ValueError(
            "Provide a non-empty topic or at least one non-empty few_shot_examples entry."
        )


class GenerateQuestionRequest(BaseModel):
    model: str
    topic: str = Field(default="", max_length=2000)
    question: MultipleChoiceQuestion
    comment: str = ""

    @field_validator("topic")
    @classmethod
    def strip_topic(cls, v: object) -> str:
        if not isinstance(v, str):
            raise TypeError("topic must be a string")
        return v.strip()

    @field_validator("comment", mode="before")
    @classmethod
    def normalize_comment(cls, v: object) -> str:
        if v is None:
            return ""
        if not isinstance(v, str):
            raise TypeError("comment must be a string")
        s = v.strip()
        if len(s) > 2000:
            raise ValueError("comment must be at most 2000 characters after trim")
        return s
