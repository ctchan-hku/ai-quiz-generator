from pydantic import BaseModel

from app.modules.generation.models.mc_question import MultipleChoiceQuestion


class GeneratedTest(BaseModel):
    __test__ = False

    questions: list[MultipleChoiceQuestion]
