from pydantic import BaseModel

from app.modules.generation.models.mc_question import MultipleChoiceQuestion


class Test(BaseModel):
    __test__ = False

    questions: list[MultipleChoiceQuestion]
