from fastapi import Request

from app.features.workspace.knowledge_base.repository import KnowledgeDocumentRepository
from app.features.workspace.knowledge_base.service import KnowledgeBaseService


def get_knowledge_base_service(request: Request) -> KnowledgeBaseService:
    store = KnowledgeDocumentRepository()
    return KnowledgeBaseService(repository=store)
