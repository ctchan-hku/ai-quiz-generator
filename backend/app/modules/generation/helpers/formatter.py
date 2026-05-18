from app.modules.generation.models import MultipleChoiceQuestion


def format_topic(topic: str) -> str:
    t = topic.strip()
    return f"Topic domain boundary: {t}" if t else ""


def _option_line_label(option_index: int) -> str:
    if option_index < 26:
        return chr(ord("A") + option_index)
    return str(option_index + 1)


def format_question(question: MultipleChoiceQuestion) -> str:
    lines = [
        f"question_type: {question.question_type}",
        f"question: {question.question}",
        "options:",
    ]
    for i, option in enumerate(question.options):
        label = _option_line_label(i)
        lines.append(f"  {label}. {option}")
    lines.append(f"correct_indices: {question.correct_indices}")
    lines.append(f"explanation: {question.explanation}")
    return "\n".join(lines)
