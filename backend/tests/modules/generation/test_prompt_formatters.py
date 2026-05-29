from app.modules.generation.llm.question_editor.prompts import (
    TOPIC_CONTEXT,
    format_question_block,
)
from app.modules.generation.llm.v1.test_generator_prompts import (
    TOPIC_CONTEXT as V1_TOPIC_CONTEXT,
)
from app.modules.generation.models import MultipleChoiceQuestion


def test_topic_context_wraps_non_empty_topic():
    assert TOPIC_CONTEXT.format(topic="Biology") == "Topic domain boundary: Biology"
    assert V1_TOPIC_CONTEXT.format(topic="Biology") == "Topic domain boundary: Biology"


def test_topic_context_skipped_for_blank_topic():
    topic = "   "
    trimmed = topic.strip()
    context = TOPIC_CONTEXT.format(topic=trimmed) if trimmed else ""
    assert context == ""


def test_format_question_block_includes_question_fields():
    question = MultipleChoiceQuestion(
        question="What is 2 + 2?",
        options=["3", "4"],
        correct_indices=[1],
        explanation="2 + 2 = 4",
    )
    block = format_question_block(question)
    assert "question: What is 2 + 2?" in block
    assert "A. 3" in block
    assert "B. 4" in block
    assert "correct_indices: [1]" in block
    assert "explanation: 2 + 2 = 4" in block
