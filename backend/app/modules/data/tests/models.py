from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TestRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    __test__ = False

    id: str
    name: str
    questions: list[Any] = Field(default_factory=list)
    grade_cutoff: list[Any] = Field(default_factory=list)


class TestListResponse(BaseModel):
    __test__ = False

    tests: list[TestRecord] = Field(default_factory=list)
