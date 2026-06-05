from pydantic import BaseModel


class SearchResult(BaseModel):
    score: float
