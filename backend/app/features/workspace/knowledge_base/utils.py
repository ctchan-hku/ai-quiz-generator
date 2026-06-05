from langchain_core.documents import Document

from app.features.workspace.document_ingestion.models import DocumentChunk


def chunks_to_documents(chunks: list[DocumentChunk]) -> list[Document]:
    return [
        Document(
            page_content=chunk.content,
            metadata={
                "document_id": chunk.document_id or "",
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
            },
        )
        for chunk in chunks
    ]
