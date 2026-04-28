"""User-authored quiz instructions (distinct from few-shot style examples)."""

from fastapi import HTTPException

from app.services.prompt_sections.section_formatter import SectionFormatter

USER_INSTRUCTIONS_MAX = 5
USER_INSTRUCTION_LINE_MAX_CHARS = 400


class UserInstructions:
    """Implements :class:`SectionFormatter` for optional ``user_instructions`` on generate quiz."""

    def normalize(self, raw: list[str] | None) -> list[str]:
        if raw is None:
            return []
        out: list[str] = []
        for s in raw:
            t = s.strip()
            if not t:
                continue
            if len(t) > USER_INSTRUCTION_LINE_MAX_CHARS:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Each user instruction line must be at most "
                        f"{USER_INSTRUCTION_LINE_MAX_CHARS} characters after trim"
                    ),
                )
            out.append(t)
        if len(out) > USER_INSTRUCTIONS_MAX:
            raise HTTPException(
                status_code=422,
                detail=f"At most {USER_INSTRUCTIONS_MAX} user instruction lines allowed",
            )
        return out

    def format_section(self, lines: list[str]) -> str:
        """Numbered block only; :class:`~app.services.llm.full_quiz.FullQuizLlm` prepends MCQ schema text."""
        if not lines:
            return ""
        body_lines = ["Additional quiz instructions:"]
        for i, text in enumerate(lines, start=1):
            body_lines.append(f"{i}. {text}")
        return "\n".join(body_lines)


USER_INSTRUCTIONS_FORMATTER: SectionFormatter = UserInstructions()
