import re

import fitz

from app.features.workspace.document_ingestion.models import (
    ImageBlock,
    ParsedDocument,
    ParsedPage,
    TextBlock,
)


class DocumentParser:
    """Extract and classify PDF content blocks."""

    def parse(self, pdf_path: str) -> ParsedDocument:
        doc = fitz.open(pdf_path)
        try:
            return self._parse_document(doc)
        finally:
            doc.close()

    def parse_bytes(self, pdf_bytes: bytes) -> ParsedDocument:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            return self._parse_document(doc)
        finally:
            doc.close()

    def _parse_document(self, doc: fitz.Document) -> ParsedDocument:
        pages: list[ParsedPage] = []
        for page_num, page in enumerate(doc, start=1):
            blocks = page.get_text("dict")["blocks"]
            parsed_blocks: list[TextBlock | ImageBlock] = []
            for block in blocks:
                if block["type"] == 0:
                    parsed_blocks.append(self._parse_text_block(block))
                elif block["type"] == 1:
                    parsed_blocks.append(self._parse_image_block(block, page_num))
            pages.append(
                ParsedPage(
                    page_number=page_num,
                    blocks=parsed_blocks,
                    width=page.rect.width,
                    height=page.rect.height,
                ),
            )
        return ParsedDocument(pages=pages, total_pages=len(doc))

    def _parse_text_block(self, block: dict) -> TextBlock:
        text = " ".join(
            span["text"]
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        )
        font_size = self._get_dominant_font_size(block)
        is_bold = self._check_if_bold(block)
        content_type = self._classify_content(text, font_size, is_bold)
        return TextBlock(
            text=text,
            content_type=content_type,
            font_size=font_size,
            is_bold=is_bold,
            bbox=block["bbox"],
        )

    def _classify_content(self, text: str, font_size: float, is_bold: bool) -> str:
        if font_size >= 16 or (is_bold and font_size >= 14):
            return "heading"
        if text.strip().startswith(("-", "•", "*", "◦")):
            return "bullet"
        if re.match(r"^\d+[\.\)]\s", text.strip()):
            return "numbered_item"
        if len(text.split()) < 10 and text.endswith(":"):
            return "label"
        return "body"

    def _get_dominant_font_size(self, block: dict) -> float:
        sizes = [
            span["size"]
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        ]
        return max(sizes) if sizes else 12.0

    def _check_if_bold(self, block: dict) -> bool:
        flags = [
            span["flags"]
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        ]
        return any(f & 16 for f in flags)

    def _parse_image_block(self, block: dict, page_num: int) -> ImageBlock:
        return ImageBlock(
            page_number=page_num,
            bbox=block["bbox"],
        )
