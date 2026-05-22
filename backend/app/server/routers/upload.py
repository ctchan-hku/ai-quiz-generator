from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.modules.data.upload.helpers import parse_pdf_bytes
from app.modules.data.upload.models import ParsedPdfDocument, UploadDocumentsResponse

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
    """Accept multiple PDF uploads and return parsed text chunks per file."""
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
            raise HTTPException(status_code=422, detail="Each uploaded file must have a filename")

        pdf_bytes = await upload.read()
        chunks = parse_pdf_bytes(pdf_bytes)
        documents.append(ParsedPdfDocument(filename=upload.filename, chunks=chunks))

    return UploadDocumentsResponse(documents=documents)
