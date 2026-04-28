"""LLM-facing text derived from question models: type labels for user lines, and stem dump for regen prompts."""

from typing import get_args

from pydantic.fields import PydanticUndefined

from app.models.schemas import BaseQuestion, MultipleChoiceQuestion


def question_type_literal(question_class: type[BaseQuestion]) -> str:
    field = question_class.model_fields["question_type"]
    if field.default is not None and field.default is not PydanticUndefined:
        return str(field.default)
    args = get_args(field.annotation)
    if args:
        return str(args[0])
    raise TypeError(f"Cannot resolve question_type for {question_class.__name__}")


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
