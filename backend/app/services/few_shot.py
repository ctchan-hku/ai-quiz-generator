"""Few-shot / style examples for full-quiz generation (request validation and prompts)."""

from fastapi import HTTPException

FEW_SHOT_MAX_EXAMPLES = 3
FEW_SHOT_MAX_CHARS = 2000


def normalize_few_shot_examples(raw: list[str] | None) -> list[str]:
    """Return up to 3 trimmed non-empty strings, or raise 422 for invalid input."""
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


def format_few_shot_system_section(examples: list[str]) -> str:
    """Append to the system message when examples is non-empty (caller checks)."""
    intro = (
        "User-provided style examples (match tone, difficulty, and format; do not copy the examples "
        "verbatim into your quiz questions—write new items for the topic. Your output must still be only "
        "the required JSON object).\n"
    )
    lines = [intro]
    for i, text in enumerate(examples, start=1):
        lines.append(f"Example {i}:\n{text}")
    return "\n".join(lines)
