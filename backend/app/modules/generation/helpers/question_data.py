"""LLM-facing text derived from question models: type labels for user lines, and stem dump for regen prompts."""

from app.modules.generation.models import MultipleChoiceQuestion


def question_type_literal(question_class: type[MultipleChoiceQuestion]) -> str:
    _ = question_class
    return "multiple_choice"


def format_topic(topic: str) -> str:
    """Shared one-line # Context for quiz flows when the user supplied a non-empty topic."""
    t = topic.strip()
    return (
        f"Topic domain boundary: {t}"
        if t
        else ""
    )


def _option_line_label(option_index: int) -> str:
    """Letter labels A-Z for the first 26 options, then 27, 28, ... if ever needed."""
    if option_index < 26:
        return chr(ord("A") + option_index)
    return str(option_index + 1)


def format_question(question: MultipleChoiceQuestion) -> str:
    """Multi-line text block of the target question (for regen / improve prompts)."""
    data = question.model_dump()
    lines = [
        f"question_type: {data['question_type']}",
        f"question: {data['question']}",
        "options:",
    ]
    for i, option in enumerate(data["options"]):
        label = _option_line_label(i)
        lines.append(f"  {label}. {option}")
    lines.append(f"correct_indices: {data['correct_indices']}")
    lines.append(f"explanation: {data['explanation']}")
    return "\n".join(lines)
