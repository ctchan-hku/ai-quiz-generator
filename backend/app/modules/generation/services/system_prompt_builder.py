from abc import ABC, abstractmethod
from typing import ClassVar

from app.modules.generation.config.prompts import JSON_OUTPUT_RULES


class SystemPromptBuilder(ABC):
    _SPECIAL_SECTION_KEYS: ClassVar[frozenset[str]] = frozenset(
        {"role", "output_format"},
    )

    _SYSTEM_SECTIONS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("role", "Role"),
        ("guidelines", "Guidelines"),
        ("context", "Context"),
        ("requirements", "Requirements"),
        ("examples", "Examples"),
        ("chain_of_thought", "Chain of Thought"),
        ("output_format", "Output Format"),
    )

    @property
    @abstractmethod
    def role_definition(self) -> str: ...

    @abstractmethod
    def structured_json_format(self) -> str: ...

    def output_format(self) -> str:
        schema = self.structured_json_format().strip()
        return f"{JSON_OUTPUT_RULES}\n\n{schema}"

    def _system_prompt(self, **sections: str) -> str:
        variable_keys = tuple(
            key
            for key, _ in self._SYSTEM_SECTIONS
            if key not in self._SPECIAL_SECTION_KEYS
        )
        allowed = frozenset(variable_keys)
        unknown = frozenset(sections) - allowed
        if unknown:
            raise TypeError(
                f"_system_prompt: unknown keys {sorted(unknown)!r}; "
                f"allowed {sorted(allowed)!r}",
            )

        raw_bodies: dict[str, str] = {
            "role": self.role_definition,
            "output_format": self.output_format(),
        }
        for key in variable_keys:
            raw_bodies[key] = sections.get(key, "")

        parts: list[str] = []
        for field, heading in self._SYSTEM_SECTIONS:
            body = raw_bodies[field].strip()
            if not body:
                continue
            parts.append(f"# {heading}\n{body}")
        return "\n\n".join(parts)


__all__ = ["SystemPromptBuilder"]
