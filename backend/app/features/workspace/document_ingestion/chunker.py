from app.features.workspace.document_ingestion.models import (
    DocumentChunk,
    ParsedDocument,
    TextBlock,
)


class DocumentChunker:
    """Split parsed document content into embedding-ready chunks."""

    def __init__(self, chunk_size: int = 400, overlap: int = 80):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, parsed_doc: ParsedDocument) -> list[DocumentChunk]:
        all_chunks: list[DocumentChunk] = []
        for page in parsed_doc.pages:
            page_text = self._assemble_page_text(page.blocks)
            all_chunks.extend(
                self._split_into_chunks(
                    text=page_text,
                    page_number=page.page_number,
                ),
            )
        return self._add_overlap(all_chunks)

    def _assemble_page_text(self, blocks: list) -> str:
        parts: list[str] = []
        for block in blocks:
            if isinstance(block, TextBlock):
                if block.content_type == "heading":
                    parts.append(f"\n\n{block.text}\n\n")
                elif block.content_type == "bullet":
                    parts.append(f"- {block.text}\n")
                else:
                    parts.append(f"{block.text}\n")
        return "".join(parts)

    def _split_into_chunks(
        self,
        text: str,
        page_number: int,
    ) -> list[DocumentChunk]:
        text = text.strip()
        if not text:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_index = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                space = text.rfind(" ", start, end)
                if space > start:
                    end = space
            segment = text[start:end].strip()
            if segment:
                chunk_index += 1
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"page_{page_number}_chunk_{chunk_index}",
                        page_number=page_number,
                        content=segment,
                        type="text",
                    ),
                )
            start = end if end > start else start + 1
        return chunks

    def _add_overlap(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        if not chunks or self.overlap <= 0:
            return chunks

        overlapped: list[DocumentChunk] = []
        for index, chunk in enumerate(chunks):
            content = chunk.content
            if index > 0:
                previous = chunks[index - 1].content
                prefix = (
                    previous[-self.overlap :]
                    if len(previous) > self.overlap
                    else previous
                )
                content = f"{prefix}{content}"
            overlapped.append(chunk.model_copy(update={"content": content}))
        return overlapped
