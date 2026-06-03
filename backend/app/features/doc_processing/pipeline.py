from app.features.doc_processing.chunker import DocumentChunker
from app.features.doc_processing.parser import DocumentParser
from app.features.doc_processing.types import DocumentChunk, ParsedDocument


class DocumentPipeline:
    """Orchestrates PDF parsing then chunking for downstream AI use."""

    def __init__(
        self,
        *,
        chunk_size: int = 400,
        overlap: int = 80,
    ) -> None:
        self.parser = DocumentParser()
        self.chunker = DocumentChunker(chunk_size=chunk_size, overlap=overlap)

    def process(self, pdf_path: str, document_id: str) -> list[DocumentChunk]:
        parsed_doc = self.parser.parse(pdf_path)
        return self._chunk_and_tag(parsed_doc, document_id)

    def process_bytes(self, pdf_bytes: bytes, document_id: str) -> list[DocumentChunk]:
        parsed_doc = self.parser.parse_bytes(pdf_bytes)
        return self._chunk_and_tag(parsed_doc, document_id)

    def _chunk_and_tag(
        self,
        parsed_doc: ParsedDocument,
        document_id: str,
    ) -> list[DocumentChunk]:
        chunks = self.chunker.chunk(parsed_doc)
        return [
            chunk.model_copy(update={"document_id": document_id}) for chunk in chunks
        ]
