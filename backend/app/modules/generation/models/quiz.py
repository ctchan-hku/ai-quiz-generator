from pydantic import BaseModel

from app.modules.generation.models.mc_question import MultipleChoiceQuestion


class Quiz(BaseModel):
    questions: list[MultipleChoiceQuestion]
