"""Collection of MCQs produced by generation pipelines.

Not the HTTP response type; see :class:`~app.modules.generation.models.responses.QuizResponse`.
"""

from pydantic import BaseModel

from app.modules.generation.models.mc_question import MultipleChoiceQuestion


class Quiz(BaseModel):
    questions: list[MultipleChoiceQuestion]
