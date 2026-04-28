"""Structural contract for optional list-shaped system-prompt segments (normalize HTTP input + render block)."""

from abc import ABC, abstractmethod


class SectionFormatter(ABC):
    """Normalize `list[str]` request fields and format the segment appended after MCQ schema text."""

    @abstractmethod
    def normalize(self, raw: list[str] | None) -> list[str]:
        """Trimmed non-empty lines, or HTTP 422 for invalid payloads."""

    @abstractmethod
    def format_section(self, lines: list[str]) -> str:
        """Format segment text (no concatenation with question-class `instructions`; caller merges)."""
