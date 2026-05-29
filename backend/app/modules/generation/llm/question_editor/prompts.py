from app.modules.generation.config.mc_question import (
    MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS,
)
from app.modules.generation.models import MultipleChoiceQuestion

REWRITE_HINT = f"""
When reviewing your output, verify the following:
1. Fact-check: Is each identified correct answer objectively true?
2. Stem: Is the question stem unambiguous, unnumbered, and aligned with the marked correct option(s)?
3. Distractors: Are incorrect options plausible relative to the stem (same topic/vocabulary), not absurd?
4. Explanation: Does it use numbered or clearly labeled deduction steps—not a vague single sentence?
5. Length: Is each explanation roughly within ~{MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS} characters unless more is clearly needed?
"""


def format_topic_context(topic: str) -> str:
    trimmed = topic.strip()
    return f"Topic domain boundary: {trimmed}" if trimmed else ""


def _option_line_label(option_index: int) -> str:
    if option_index < 26:
        return chr(ord("A") + option_index)
    return str(option_index + 1)


def format_question_block(question: MultipleChoiceQuestion) -> str:
    lines = [
        f"question_type: {question.question_type}",
        f"question: {question.question}",
        "options:",
    ]
    for index, option in enumerate(question.options):
        label = _option_line_label(index)
        lines.append(f"  {label}. {option}")
    lines.append(f"correct_indices: {question.correct_indices}")
    lines.append(f"explanation: {question.explanation}")
    return "\n".join(lines)
