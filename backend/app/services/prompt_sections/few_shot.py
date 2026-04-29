"""Few-shot / style examples for full-quiz generation."""

from fastapi import HTTPException

from app.services.prompt_sections.section_formatter import SectionFormatter

FEW_SHOT_MAX_EXAMPLES = 3
FEW_SHOT_MAX_CHARS = 2000


class FewShotExamples(SectionFormatter):
    """Implements :class:`SectionFormatter` for optional ``few_shot_examples`` on generate quiz."""

    def normalize(self, raw: list[str] | None) -> list[str]:
        if raw is None:
            return []
        out: list[str] = []
        for s in raw:
            t = s.strip()
            if not t:
                continue
            if len(t) > FEW_SHOT_MAX_CHARS:
                raise HTTPException(
                    status_code=422,
                    detail=f"Each few_shot example must be at most {FEW_SHOT_MAX_CHARS} characters",
                )
            out.append(t)
        if len(out) > FEW_SHOT_MAX_EXAMPLES:
            raise HTTPException(
                status_code=422,
                detail=f"At most {FEW_SHOT_MAX_EXAMPLES} few_shot examples allowed",
            )
        return out

    def format_section(self, examples: list[str]) -> str:
        if not examples:
            return ""
        intro = (
            "These examples are reference material: match their scenario, format, and level of detail "
            "when you write new questions. Use them to stay consistent with how a good item should look "
            "and read. Do not copy them verbatim—create original questions for the requested scope.\n"
        )
        lines = [intro]
        for i, text in enumerate(examples, start=1):
            lines.append(f"Example {i}:\n{text}")
        return "\n".join(lines)


FEW_SHOT_FORMATTER: SectionFormatter = FewShotExamples()
