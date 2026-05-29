from pydantic import BaseModel

from app.features.generation.models.mc_question import MultipleChoiceQuestion


class GeneratedTest(BaseModel):
    __test__ = False

    questions: list[MultipleChoiceQuestion]
