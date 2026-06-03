from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class TextBlock:
    text: str
    content_type: str
    font_size: float
    is_bold: bool
    bbox: tuple[float, float, float, float]


@dataclass
class ImageBlock:
    page_number: int
    bbox: tuple[float, float, float, float]
    content_type: str = "image"


@dataclass
class ParsedPage:
    page_number: int
    blocks: list[TextBlock | ImageBlock]
    width: float
    height: float


@dataclass
class ParsedDocument:
    pages: list[ParsedPage]
    total_pages: int


class DocumentChunk(BaseModel):
    chunk_id: str
    page_number: int = Field(ge=1)
    content: str
    type: str = "text"
    document_id: str | None = None
