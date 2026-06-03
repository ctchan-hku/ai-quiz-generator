from pydantic import BaseModel, Field


class PdfChunk(BaseModel):
    chunk_id: str
    page_number: int = Field(ge=1)
    content: str
    type: str = "text"


class ParsedPdfDocument(BaseModel):
    filename: str
    chunk_count: int = Field(ge=0)


class UploadDocumentsResponse(BaseModel):
    documents: list[ParsedPdfDocument] = Field(default_factory=list)
