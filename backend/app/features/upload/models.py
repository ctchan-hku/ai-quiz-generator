from pydantic import BaseModel, Field


class PdfChunk(BaseModel):
    chunk_id: str
    page_number: int = Field(ge=1)
    content: str
    type: str = "text"
