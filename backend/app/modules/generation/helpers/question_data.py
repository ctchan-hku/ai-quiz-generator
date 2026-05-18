from app.modules.generation.models import MultipleChoiceQuestion


def question_type_literal(question_class: type[MultipleChoiceQuestion]) -> str:
    _ = question_class
    return "multiple_choice"


def format_topic(topic: str) -> str:
    t = topic.strip()
    return f"Topic domain boundary: {t}" if t else ""


def _option_line_label(option_index: int) -> str:
    if option_index < 26:
        return chr(ord("A") + option_index)
    return str(option_index + 1)


def format_question(question: MultipleChoiceQuestion) -> str:
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
