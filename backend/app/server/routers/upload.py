import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.features.auth.models import AuthenticatedUser
from app.features.workspace.knowledge_base.models import KnowledgeDocumentSummary
from app.features.workspace.knowledge_base.service import KnowledgeBaseService
from app.server.dependencies.auth import get_current_user
from app.server.dependencies.knowledge_base import get_knowledge_base_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

PDF_CONTENT_TYPES = frozenset({"application/pdf"})


class UploadDocumentsResponse(BaseModel):
    documents: list[KnowledgeDocumentSummary] = Field(default_factory=list)


def _is_pdf(upload: UploadFile) -> bool:
    if upload.filename and upload.filename.lower().endswith(".pdf"):
        return True
    return upload.content_type in PDF_CONTENT_TYPES


@router.post("/upload/documents", response_model=UploadDocumentsResponse)
async def upload_documents(
    files: Annotated[list[UploadFile], File()],
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> UploadDocumentsResponse:
    if not files:
        raise HTTPException(status_code=422, detail="At least one PDF file is required")

    documents: list[KnowledgeDocumentSummary] = []
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
        summary = service.ingest(pdf_bytes, upload.filename, user.user_id)
        logger.info(
            "Ingested PDF %s for user %s: %d chunk(s), doc_id=%s",
            upload.filename,
            user.user_id,
            summary.chunk_count,
            summary.id,
        )
        documents.append(summary)

    return UploadDocumentsResponse(documents=documents)
