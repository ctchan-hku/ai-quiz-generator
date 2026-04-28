"""Structural contract for optional list-shaped system-prompt segments (normalize HTTP input + render block)."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class SectionFormatter(Protocol):
    """Normalize `list[str]` request fields and format the segment appended after MCQ schema text."""

    def normalize(self, raw: list[str] | None) -> list[str]:
        """Trimmed non-empty lines, or HTTP 422 for invalid payloads."""

    def format_section(self, lines: list[str]) -> str:
        """Format segment text (no concatenation with question-class `instructions`; caller merges)."""
