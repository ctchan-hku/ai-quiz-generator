from pydantic import BaseModel

from app.core.domain.base import ResponseNrl


class QuestionRecord(BaseModel):
    id: str
    prompt: str | None = None
    type: str | None = None
    response_nrl: ResponseNrl
