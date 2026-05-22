import fitz

from app.modules.data.upload.models import PdfChunk


def _chunks_from_document(doc: fitz.Document) -> list[PdfChunk]:
    chunks: list[PdfChunk] = []
    for page_num, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            chunks.append(
                PdfChunk(
                    chunk_id=f"slide_{page_num + 1}",
                    page_number=page_num + 1,
                    content=text,
                    type="text",
                ),
            )
    return chunks


def parse_pdf(pdf_path: str) -> list[PdfChunk]:
    """Extract text per slide (page = slide) from a PDF file path."""
    doc = fitz.open(pdf_path)
    try:
        return _chunks_from_document(doc)
    finally:
        doc.close()


def parse_pdf_bytes(pdf_bytes: bytes) -> list[PdfChunk]:
    """Extract text per slide (page = slide) from PDF bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        return _chunks_from_document(doc)
    finally:
        doc.close()
