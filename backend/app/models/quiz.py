"""Collection of MCQ items (e.g. from :class:`~app.modules.generation.llm.v1.full_quiz.FullQuizLlm` or :class:`~app.modules.generation.llm.v2.quiz_pipeline.FullQuizV2Pipeline`).

Not the HTTP response type; see `generate_responses.QuizResponse` for the API envelope.
"""

from pydantic import BaseModel

from app.models.mc_question import MultipleChoiceQuestion


class Quiz(BaseModel):
    questions: list[MultipleChoiceQuestion]
