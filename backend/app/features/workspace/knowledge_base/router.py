from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.features.auth.models import AuthenticatedUser
from app.features.workspace.knowledge_base.models import KnowledgeDocumentSummary
from app.features.workspace.knowledge_base.service import KnowledgeBaseService
from app.server.dependencies.auth import get_current_user
from app.server.dependencies.knowledge_base import get_knowledge_base_service

router = APIRouter(prefix="/api/knowledge")


@router.get("/documents", response_model=list[KnowledgeDocumentSummary])
async def list_documents(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> list[KnowledgeDocumentSummary]:
    return service.list_documents(user.user_id)


@router.patch(
    "/documents/{document_id}",
    response_model=KnowledgeDocumentSummary,
)
async def toggle_document(
    document_id: str,
    is_active: bool,
    service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> KnowledgeDocumentSummary:
    try:
        return service.toggle_document(document_id, is_active)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> None:
    try:
        service.delete_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
