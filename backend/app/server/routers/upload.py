import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

logger = logging.getLogger(__name__)

from app.features.upload.models import ParsedPdfDocument, UploadDocumentsResponse
from app.features.upload.parse_pdf import parse_pdf_bytes

router = APIRouter(prefix="/api")

PDF_CONTENT_TYPES = frozenset({"application/pdf"})


def _is_pdf(upload: UploadFile) -> bool:
    if upload.filename and upload.filename.lower().endswith(".pdf"):
        return True
    return upload.content_type in PDF_CONTENT_TYPES


@router.post("/upload/documents", response_model=UploadDocumentsResponse)
async def upload_documents(
    files: Annotated[list[UploadFile], File()],
) -> UploadDocumentsResponse:
    """Accept multiple PDF uploads; return chunk counts (content logged server-side)."""
    if not files:
        raise HTTPException(status_code=422, detail="At least one PDF file is required")

    documents: list[ParsedPdfDocument] = []
    for upload in files:
        if not _is_pdf(upload):
            raise HTTPException(
                status_code=422,
                detail=f"File '{upload.filename or 'unknown'}' is not a PDF",
            )
        if not upload.filename:
            raise HTTPException(
                status_code=422, detail="Each uploaded file must have a filename"
            )

        pdf_bytes = await upload.read()
        chunks = parse_pdf_bytes(pdf_bytes)
        logger.info(
            "Parsed PDF %s: %d chunk(s)",
            upload.filename,
            len(chunks),
        )
        for chunk in chunks:
            logger.info(
                "  [%s] page=%d type=%s content=%s",
                chunk.chunk_id,
                chunk.page_number,
                chunk.type,
                chunk.content,
            )
        documents.append(
            ParsedPdfDocument(
                filename=upload.filename,
                chunk_count=len(chunks),
            ),
        )

    return UploadDocumentsResponse(documents=documents)
