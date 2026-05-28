from pydantic import BaseModel, ConfigDict


class TestSummary(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    __test__ = False

    id: str
    name: str
    num_questions: int


class SpecificationItem(BaseModel):
    label: str
    value: int | float


class ResponseNrl(BaseModel):
    specification: list[SpecificationItem]
