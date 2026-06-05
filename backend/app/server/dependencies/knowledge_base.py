from fastapi import Request

from app.features.workspace.knowledge_base.metadata_store import KnowledgeMetadataStore
from app.features.workspace.knowledge_base.service import KnowledgeBaseService


def get_knowledge_base_service(request: Request) -> KnowledgeBaseService:
    store = KnowledgeMetadataStore()
    return KnowledgeBaseService(metadata_store=store)
