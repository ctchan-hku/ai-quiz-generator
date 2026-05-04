"""Parsed quiz shape from the LLM (internal to `FullQuizLlm` / validators).

Not the HTTP response type; see `generate_responses.QuizResponse` for the API envelope.
"""

from pydantic import BaseModel

from app.models.mc_question import MultipleChoiceQuestion


class Quiz(BaseModel):
    questions: list[MultipleChoiceQuestion]
